"""Unit tests of evaluate.py, sample.py and cards.py (run by python-units.test.mjs)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import cards  # noqa: E402
import evaluate as ev  # noqa: E402
import sample  # noqa: E402


class Metrics(unittest.TestCase):
    def test_wilson(self):
        self.assertEqual(ev.wilson(90, 100), [0.8256, 0.9448])
        self.assertEqual(ev.wilson(45, 50), [0.7864, 0.9565])
        self.assertIsNone(ev.wilson(0, 0))

    def test_precision_counts_u_against(self):
        p = ev.precision(["TP"] * 8 + ["FP"] + ["U"])
        self.assertEqual((p["n"], p["primary"], p["secondary"]), (10, 0.8, round(8 / 9, 4)))

    def test_fp_per_1000(self):
        p = ev.precision(["TP"] * 90 + ["FP"] * 8 + ["U"] * 2)
        fp = ev.fp_per_1000(p, critical_total=200, files=5000)  # density 40
        self.assertEqual(fp["densityCriticalPer1000"], 40.0)
        self.assertEqual(fp["primary"], 4.0)  # (8 + 2) / 100 × 40
        lo, hi = ev.wilson(10, 100)
        self.assertEqual(fp["primaryCI95"], [round(40 * lo, 4), round(40 * hi, 4)])
        self.assertEqual(fp["secondary"], round(40 * 8 / 98, 4))
        self.assertEqual(ev.fp_per_1000(ev.precision([]), 0, 1000)["primary"], 0.0)

    def test_criterion1_needs_both_n_and_point_estimate(self):
        perfect = ev.precision(["TP"] * 49)
        self.assertEqual(ev.criterion1(perfect, 49, 50)["status"], "NOT MET")
        self.assertEqual(ev.criterion1(ev.precision(["TP"] * 45 + ["FP"] * 5), 50, 50)["status"], "MET")
        self.assertEqual(ev.criterion1(ev.precision(["TP"] * 44 + ["FP"] * 5 + ["U"]), 50, 50)["status"], "NOT MET")
        self.assertEqual(ev.criterion1(ev.precision(["TP"] * 100), 99, 100)["reasons"], ["only 99 CRITICAL reviewed, 100 required"])

    def test_criterion2_threshold(self):
        self.assertTrue(ev.criterion2({"primary": 5.0})["met"])
        self.assertFalse(ev.criterion2({"primary": 5.0001})["met"])
        self.assertFalse(ev.criterion2({"primary": None})["met"])

    def test_kappa(self):
        self.assertEqual(ev.kappa([("TP", "TP"), ("FP", "FP")])["cohenKappa"], 1.0)
        self.assertEqual(ev.kappa([])["n"], 0)

    def test_cluster_bootstrap_is_deterministic(self):
        repos = [{"critical": 10, "files": 100, "reviewed": 5, "bad": 1}, {"critical": 2, "files": 400, "reviewed": 2, "bad": 0},
                 {"critical": 0, "files": 300, "reviewed": 0, "bad": 0}]
        a, b = ev.cluster_bootstrap(repos), ev.cluster_bootstrap(repos)
        self.assertEqual(a, b)
        self.assertLessEqual(a[0], a[1])


def synthetic(n_java=50, n_py=100):
    def f(lang, i, repo):
        return {"id": f"{'J' if lang == 'java' else 'P'}{i:03d}", "language": lang, "repo": repo, "ruleId": "R", "subpool": "java" if lang == "java" else "python-A",
                "families": ["KAFKA"] if lang == "java" else [], "severity": "critical"}
    findings = [f("java", i, "j/one") for i in range(1, n_java + 1)] + [f("python", i, "p/one") for i in range(1, n_py + 1)]
    rs = {"languages": {"java": {"totalCritical": n_java, "reviewed": n_java, "required": 50, "method": "every", "corpusFrozenReason": "x"},
                        "python": {"totalCritical": n_py, "reviewed": n_py, "required": 100, "method": "every", "corpusFrozenReason": "y"}},
          "findings": findings}
    corpora = {"java": {"processed": [{"status": "included", "full_name": "j/one", "files": {"java": 10000, "python": 0}}]},
               "python": {"processed": [{"status": "included", "full_name": "p/one", "files": {"java": 0, "python": 5000}}]}}
    reports = {"java": {"j/one": {"findings": [{"severity": "critical", "language": "java"}] * n_java}},
               "python": {"p/one": {"findings": [{"severity": "critical", "language": "python"}] * n_py + [{"severity": "warning", "language": "python"}]}}}
    return rs, corpora, reports


class Evaluate(unittest.TestCase):
    def test_official_verdicts_are_joaquins_only(self):
        rs, corpora, reports = synthetic()
        joaquin = {f["id"]: {"verdict": "TP"} for f in rs["findings"]}
        del joaquin["P007"]
        claude = {f["id"]: {"verdict": "TP"} for f in rs["findings"]}
        with self.assertRaises(SystemExit):
            ev.evaluate(rs, corpora, reports, joaquin, claude)

    def test_claude_never_counts_and_languages_are_separate(self):
        rs, corpora, reports = synthetic()
        joaquin = {f["id"]: {"verdict": "TP" if f["language"] == "java" else ("TP" if int(f["id"][1:]) <= 80 else "FP")} for f in rs["findings"]}
        claude = {f["id"]: {"verdict": "FP"} for f in rs["findings"]}
        m = ev.evaluate(rs, corpora, reports, joaquin, claude)
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["criterion1"]["status"], "NOT MET")  # 0.80
        self.assertEqual(m["languages"]["python"]["fpPer1000"]["primary"], 4.0)  # 20/100 × 20
        self.assertEqual(m["languages"]["python"]["criterion2"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["volume"]["per1000"]["warning"], 0.2)
        self.assertEqual(m["agreementClaudeSealed"]["counts"], "never")
        self.assertEqual(m, ev.evaluate(rs, corpora, reports, joaquin, claude) | {})
        without = ev.evaluate(rs, corpora, reports, joaquin)
        self.assertEqual(without["languages"], m["languages"])
        self.assertIn("does **not** show with 95 % confidence", ev.render(m))

    def test_java_short_of_the_sample_is_not_met(self):
        rs, corpora, reports = synthetic(n_java=30)
        joaquin = {f["id"]: {"verdict": "TP"} for f in rs["findings"]}
        m = ev.evaluate(rs, corpora, reports, joaquin)
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "NOT MET")
        self.assertEqual(m["languages"]["java"]["precision"]["primary"], 1.0)


class Sample(unittest.TestCase):
    def test_draw_java_first_and_caps(self):
        def mk(lang, n):
            out = [{"repo": f"r/{i % 7}", "file": f"f{i}", "line": i, "ruleId": "R", "message": "m"} for i in range(n)]
            out.sort(key=sample.sort_key)
            for i, f in enumerate(out, 1):
                f["id"] = f"{sample.PREFIX[lang]}{i:03d}"
            return out
        by_lang = {"java": mk("java", 30), "python": mk("python", 120)}
        chosen, method = sample.draw(by_lang, sample.random.Random(sample.SEED_REVIEW))
        self.assertEqual(len(chosen["java"]), 30)
        self.assertEqual(method["java"], "every CRITICAL finding")
        self.assertEqual(len(chosen["python"]), 100)
        again, _ = sample.draw(by_lang, sample.random.Random(sample.SEED_REVIEW))
        self.assertEqual([f["id"] for f in chosen["python"]], [f["id"] for f in again["python"]])
        self.assertEqual((sample.SEED_REVIEW, sample.SEED_REPEAT, sample.REQUIRED), (20261021, 20261023, {"java": 50, "python": 100}))

    def test_repeat_sample(self):
        fs = [{"id": f"P{i:03d}"} for i in range(1, 101)]
        a = sample.repeat_sample(fs)
        self.assertEqual(len(a), 10)
        self.assertEqual(a, sample.repeat_sample(list(reversed(fs))))


PY_SRC = '''import asyncio

def helper():
    return 1

@app.get("/x")
async def handler(req):
    data = open("f").read()
    return data
'''

JAVA_SRC = '''package demo;
/* a { brace in a comment */
@Service
public class OrderService {
    private final String s = "{ not a block";
    public OrderService(Repo r) {
        this.r = r;
    }

    @Async("pool")
    public CompletableFuture<Void> process(String id) throws IOException {
        Runnable x = () -> {
            client.get().block();
        };
        new Thread() { public void run() { foo(); } };
        if (id == null) { return null; }
        return CompletableFuture.completedFuture(future.get());
    }
}
'''


class Cards(unittest.TestCase):
    def test_classify_path(self):
        self.assertEqual(cards.classify_path("src/test/java/A.java"), "test")
        self.assertEqual(cards.classify_path("pkg/tests/x.py"), "test")
        self.assertEqual(cards.classify_path("pkg/test_x.py"), "test")
        self.assertEqual(cards.classify_path("src/main/java/OrderServiceTest.java"), "test")
        self.assertEqual(cards.classify_path("scripts/run.py"), "example-or-script")
        self.assertEqual(cards.classify_path("pyapp/examples/a.py"), "example-or-script")
        self.assertEqual(cards.classify_path("src/main/java/com/example/demo/A.java"), "main")
        self.assertEqual(cards.classify_path("app/service.py"), "main")
        self.assertEqual(cards.classify_path("examples/src/main/java/demo/A.java"), "example-or-script")

    def test_python_enclosing(self):
        self.assertEqual(cards.python_enclosing(PY_SRC, 8), ("handler", 6, 9))
        self.assertEqual(cards.python_enclosing(PY_SRC, 4), ("helper", 3, 4))
        self.assertIsNone(cards.python_enclosing(PY_SRC, 1))
        self.assertIsNone(cards.python_enclosing("def (:", 1))

    def test_java_enclosing(self):
        self.assertEqual(cards.java_enclosing(JAVA_SRC, 13), ("process", 10, 18))  # inside a lambda
        self.assertEqual(cards.java_enclosing(JAVA_SRC, 17), ("process", 10, 18))
        self.assertEqual(cards.java_enclosing(JAVA_SRC, 7), ("OrderService", 6, 8))  # constructor
        self.assertEqual(cards.java_enclosing(JAVA_SRC, 15)[0], "run")  # anonymous class method, innermost
        self.assertIsNone(cards.java_enclosing(JAVA_SRC, 5))  # field

    def test_card_lists_every_match_and_has_no_assessment(self):
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            subprocess.run(["git", "init", "-q"], cwd=d, check=True)
            Path(d, "app").mkdir()
            Path(d, "tests").mkdir()
            Path(d, "app", "api.py").write_text(PY_SRC)
            Path(d, "app", "main.py").write_text("from app.api import handler\nrouter.add(handler)\nhandler_other = 1\n")
            Path(d, "tests", "test_api.py").write_text("await handler(req)\n")
            subprocess.run(["git", "add", "-A"], cwd=d, check=True)
            subprocess.run(["git", "commit", "-qm", "x"], cwd=d, check=True, env=env)
            matches = cards.literal_matches(d, "handler")
            self.assertEqual([(m["path"], m["line"], m["class"]) for m in matches],
                             [("app/api.py", 7, "main"), ("app/main.py", 1, "main"), ("app/main.py", 2, "main"), ("tests/test_api.py", 1, "test")])
            f = {"id": "P001", "language": "python", "repo": "o/r", "commit": "c" * 40, "file": "app/api.py", "line": 8,
                 "ruleId": "PYVIBE-009", "engine": "python-vibe-guard", "severity": "critical", "message": "MESSAGE"}
            card = cards.render_card(f, PY_SRC, matches)
            self.assertIn("**4 matches**, all listed", card)
            self.assertIn('>8      data = open("f").read()', card)
            self.assertIn("https://github.com/o/r/tree/" + "c" * 40, card)
            template = card.replace("MESSAGE", "")
            for word in ("TP", "FP", "true positive", "false positive", "likely", "probably", "seems", "appears", "parece", "verdict"):
                self.assertNotIn(word, template, word)


if __name__ == "__main__":
    unittest.main()
