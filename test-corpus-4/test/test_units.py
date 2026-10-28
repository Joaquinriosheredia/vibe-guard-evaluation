"""Unit tests of evaluate.py, sample.py, cards.py, review_sheet.py and ai_compare.py of test-corpus-4
(run by python-units.test.mjs)."""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import ai_compare  # noqa: E402
import cards  # noqa: E402
import evaluate as ev  # noqa: E402
import review_sheet  # noqa: E402
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

    def test_cluster_bootstrap_is_deterministic(self):
        repos = [{"critical": 10, "files": 100, "reviewed": 5, "bad": 1}, {"critical": 2, "files": 400, "reviewed": 2, "bad": 0},
                 {"critical": 0, "files": 300, "reviewed": 0, "bad": 0}]
        a, b = ev.cluster_bootstrap(repos), ev.cluster_bootstrap(repos)
        self.assertEqual(a, b)
        self.assertLessEqual(a[0], a[1])


def synthetic(n_java=50, n_py=100):
    def f(lang, i, repo):
        return {"id": f"{'J' if lang == 'java' else 'P'}{i:03d}", "language": lang, "repo": repo, "ruleId": "R", "subpool": "java-A" if lang == "java" else "python-A",
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


def joaquin_of(rs, verdict_of, over=()):
    return {f["id"]: {"verdict": verdict_of(f), "overstated": f["id"] in over} for f in rs["findings"]}


class Evaluate(unittest.TestCase):
    def run_eval(self, rs, corpora, reports, verdict_of, assisted=(), over=()):
        final = ev.final_verdicts(rs["findings"], joaquin_of(rs, verdict_of, over), assisted)
        return ev.evaluate(rs, corpora, reports, final, assisted), final

    def test_joaquin_must_cover_exactly_the_review_set(self):
        rs, _, _ = synthetic()
        j = joaquin_of(rs, lambda f: "TP")
        del j["P100"]
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], j)
        j = joaquin_of(rs, lambda f: "TP")
        j["P101"] = {"verdict": "TP", "overstated": False}
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], j)

    def test_final_is_joaquin_everywhere_and_overstated_his(self):
        rs, corpora, reports = synthetic()
        m, final = self.run_eval(rs, corpora, reports, lambda f: "U" if f["id"] == "P100" else "TP", over={"P001", "J003"})
        self.assertEqual({v["source"] for v in final.values()}, {"Joaquín"})
        self.assertEqual(final["P100"]["verdict"], "U")
        self.assertEqual((m["languages"]["python"]["messageOverstated"], m["languages"]["java"]["messageOverstated"]), (1, 1))
        self.assertIn("no AI verdict", m["reviewMethod"])
        self.assertNotIn("review", m)  # no A/B summary, no audit

    def test_criterion1_has_no_audit_rule(self):
        rs, corpora, reports = synthetic()
        m, _ = self.run_eval(rs, corpora, reports, lambda f: "TP" if int(f["id"][1:]) > 5 else "FP")
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "MET")  # 45/50 = 0.90
        self.assertEqual(m["languages"]["python"]["criterion1"]["status"], "MET")  # 95/100
        self.assertFalse(any("RELIABLE" in r for lang in ("java", "python") for r in m["languages"][lang]["criterion1"]["reasons"]))

    def test_languages_are_separate(self):
        rs, corpora, reports = synthetic()
        m, _ = self.run_eval(rs, corpora, reports, lambda f: "TP" if f["language"] == "java" else ("TP" if int(f["id"][1:]) <= 80 else "FP"))
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["criterion1"]["status"], "NOT MET")  # 0.80
        self.assertEqual(m["languages"]["python"]["fpPer1000"]["primary"], 4.0)  # 20/100 × 20
        self.assertEqual(m["languages"]["python"]["criterion2"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["volume"]["per1000"]["warning"], 0.2)
        md = ev.render(m)
        self.assertIn("does **not** show with 95 % confidence", md)
        self.assertIn("reviewed by the author (Joaquín)", md)

    def test_java_short_of_the_sample_is_not_met(self):
        rs, corpora, reports = synthetic(n_java=30)
        m, _ = self.run_eval(rs, corpora, reports, lambda f: "TP")
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "NOT MET")
        self.assertEqual(m["languages"]["java"]["precision"]["primary"], 1.0)

    def test_subpool_breakdown_is_informational(self):
        rs, corpora, reports = synthetic()
        m, _ = self.run_eval(rs, corpora, reports, lambda f: "TP")
        self.assertEqual(list(m["languages"]["java"]["by_subpool"]), ["java-A"])


class EvaluateAssisted(unittest.TestCase):
    """PREREGISTRATION.md "Assistance during the review": (a) all verdicts, (b) the assisted verdicts as U;
    the less favourable decides. Applied only when REVIEW-LOG.md lists assisted IDs."""

    def both(self, verdict_of, assisted):
        rs, corpora, reports = synthetic()
        j = joaquin_of(rs, verdict_of)
        fa, fb = ev.final_verdicts(rs["findings"], j), ev.final_verdicts(rs["findings"], j, assisted)
        return ev.both(ev.evaluate(rs, corpora, reports, fa), ev.evaluate(rs, corpora, reports, fb, assisted), assisted), fa, fb

    def test_assisted_ids_read_from_review_log(self):
        log = "# Review log\n\n**Assisted IDs:** {}\n\n| date | who | IDs | question | answer |\n"
        self.assertEqual(ev.assisted_ids(log.format("none")), [])
        self.assertEqual(ev.assisted_ids(log.format("J001, P072")), ["J001", "P072"])
        for bad in (log.format("J1"), log.format("J001, J001"), log.format(""), "# no line\n", log.format("none") + log.format("none")):
            with self.assertRaises(SystemExit, msg=bad):
                ev.assisted_ids(bad)

    def test_no_assisted_ids_means_a_alone_decides(self):
        rs, corpora, reports = synthetic()
        fa = ev.final_verdicts(rs["findings"], joaquin_of(rs, lambda f: "TP"))
        m = ev.both(ev.evaluate(rs, corpora, reports, fa), None, [])
        self.assertEqual(m["criterion1"]["java"], {"a": "MET", "b": None, "status": "MET", "differs": False})
        md = ev.render_both(m)
        self.assertIn("Assisted verdicts (`REVIEW-LOG.md`): none", md)
        self.assertNotIn("(b)", md)

    def test_version_b_counts_assisted_as_u(self):
        m, fa, fb = self.both(lambda f: "TP", ["J001", "P100"])
        self.assertEqual((fa["J001"]["verdict"], fb["J001"]["verdict"], fb["J001"]["source"]), ("TP", "U", "assisted -> U"))
        self.assertEqual(fb["J002"]["source"], "Joaquín")
        self.assertEqual(m["b"]["languages"]["python"]["precision"]["U"], 1)
        self.assertEqual(m["b"]["assistedAsU"], ["J001", "P100"])
        self.assertIn("Assisted verdicts counted as U: J001, P100.", ev.render_both(m))

    def test_less_favourable_decides(self):
        # Java 50: 45 TP (0.90). Assisting one TP turns it into U: (b) 44/50 = 0.88 -> NOT MET.
        m, _, _ = self.both(lambda f: "FP" if f["language"] == "java" and int(f["id"][1:]) <= 5 else "TP", ["J010"])
        self.assertEqual(m["criterion1"]["java"], {"a": "MET", "b": "NOT MET", "status": "NOT MET", "differs": True})
        self.assertEqual(m["criterion1"]["python"]["status"], "MET")
        md = ev.render_both(m)
        self.assertIn("| java | 1 | MET | NOT MET | **NOT MET** |", md)
        self.assertIn("## (b) Assisted verdicts as U", md)

    def test_assisted_must_be_in_the_review_set(self):
        rs, _, _ = synthetic()
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], joaquin_of(rs, lambda f: "TP"), ["P999"])

    def test_seeds_of_the_preregistration(self):
        self.assertEqual((ev.SEED_CAP, ev.SEED_BOOT), (20261202, 20261203))


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
        self.assertEqual((sample.SEED_REVIEW, sample.REQUIRED), (20261201, {"java": 50, "python": 100}))
        self.assertFalse(hasattr(sample, "repeat_sample"))  # no repeatability in test-corpus-4


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
            Path(d, "build").mkdir()
            Path(d, "build", "app.so").write_bytes(b"\x00\x01 handler \x00\xff")
            subprocess.run(["git", "add", "-A"], cwd=d, check=True)
            subprocess.run(["git", "commit", "-qm", "binary"], cwd=d, check=True, env=env)
            raw = subprocess.run(["git", "grep", "-n", "-w", "-F", "-e", "handler"], cwd=d, capture_output=True, text=True).stdout
            self.assertIn("Binary file build/app.so matches", raw)  # the git output this covers
            matches = cards.literal_matches(d, "handler")
            self.assertEqual([(m["path"], m["line"], m["class"], m["text"]) for m in matches][:2],
                             [("app/api.py", 7, "main", "async def handler(req):"), ("app/main.py", 1, "main", "from app.api import handler")])
            self.assertEqual([(m["path"], m["line"], m["class"]) for m in matches],
                             [("app/api.py", 7, "main"), ("app/main.py", 1, "main"), ("app/main.py", 2, "main"),
                              ("build/app.so", None, "main"), ("tests/test_api.py", 1, "test")])
            self.assertEqual(matches[3]["text"], "binary file")
            f = {"id": "P001", "language": "python", "repo": "o/r", "commit": "c" * 40, "file": "app/api.py", "line": 8,
                 "ruleId": "PYVIBE-009", "engine": "python-vibe-guard", "severity": "critical", "message": "MESSAGE"}
            card = cards.render_card(f, PY_SRC, matches)
            self.assertIn("**5 matches**, all listed", card)
            self.assertIn("| build/app.so | — | main | `binary file` |", card)
            self.assertIn('>8      data = open("f").read()', card)
            self.assertIn("https://github.com/o/r/tree/" + "c" * 40, card)
            template = card.replace("MESSAGE", "")
            for word in ("TP", "FP", "true positive", "false positive", "likely", "probably", "seems", "appears", "parece", "verdict"):
                self.assertNotIn(word, template, word)


class CardsRecords(unittest.TestCase):
    def test_records_split_on_newline_only_and_control_chars_escaped(self):
        # DEVIATIONS.md §2: a matched line with \r or \x85 is one record, not several.
        with tempfile.TemporaryDirectory() as d:
            env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
            subprocess.run(["git", "init", "-q"], cwd=d, check=True)
            subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=d, check=True)
            Path(d, "a.css").write_bytes("x{handler:1}\ry{handler:2}\u0085z handler\n".encode("utf-8") + b"second handler line\n")
            Path(d, "b.py").write_text("def handler():\n    pass\n")
            subprocess.run(["git", "add", "-A"], cwd=d, check=True)
            subprocess.run(["git", "commit", "-qm", "x"], cwd=d, check=True, env=env)
            text_mode = subprocess.run(["git", "grep", "-n", "-w", "-F", "-e", "handler"], cwd=d, capture_output=True, text=True).stdout.splitlines()
            self.assertGreater(len(text_mode), 3)  # the old reading split the first record
            matches = cards.literal_matches(d, "handler")
            self.assertEqual([(m["path"], m["line"]) for m in matches], [("a.css", 1), ("a.css", 2), ("b.py", 1)])
            self.assertIn("\r", matches[0]["text"])
            f = {"id": "P001", "language": "python", "repo": "o/r", "commit": "c" * 40, "file": "b.py", "line": 2,
                 "ruleId": "R", "engine": "e", "severity": "critical", "message": "M"}
            card = cards.render_card(f, "def handler():\n    pass\n", matches)
            self.assertIn("| a.css | 1 | main | `x{handler:1}\\x0dy{handler:2}\\x85z handler` |", card)
            self.assertNotIn("\r", card)
            self.assertNotIn("\u0085", card)

    def test_parse_record_rejects_unparsable(self):
        with self.assertRaises(ValueError):
            cards.parse_record(b" visibility 0s 1s,")
        self.assertEqual(cards.parse_record(b"Binary file b/app.so matches")["line"], None)
        self.assertEqual(cards.parse_record(b"a/b.py:12:  x = 1")["line"], 12)


class ReviewSheet(unittest.TestCase):
    IDS = ["J001", "J002", "P001"]
    EMPTY = "- Verdict: \n- FP condition: \n- Reason (file:line): \n- Overstated: "

    def filled(self, **override):
        rows = {"J001": ("TP", "—", "a/B.java:10 runs on the @Async pool", "No"),
                "J002": ("FP", "reachability", "b/C.java:3 only called from src/test/X.java:7", "Sí"),
                "P001": ("U", "", "x.py:5 caller outside the repository", "No")}
        rows.update(override)
        text = review_sheet.render_sheet(self.IDS)
        for i, (v, c, r, o) in rows.items():
            text = text.replace(f"## {i}\n\n- Card: [cards/{i}.md](cards/{i}.md)\n{self.EMPTY}",
                                f"## {i}\n\n- Card: [cards/{i}.md](cards/{i}.md)\n- Verdict: {v}\n- FP condition: {c}\n- Reason (file:line): {r}\n- Overstated: {o}")
        return text

    def test_sheet_has_only_id_card_and_empty_fields(self):
        text = review_sheet.render_sheet(self.IDS)
        block = text.split("## J001\n", 1)[1].split("## J002", 1)[0]
        self.assertEqual(block, f"\n- Card: [cards/J001.md](cards/J001.md)\n{self.EMPTY}\n\n")
        self.assertIn("REVIEW-CRITERIA.md` v1", text)

    def test_complete_sheet_converts(self):
        out = review_sheet.parse_sheet(self.filled(), self.IDS)
        self.assertEqual([(v["id"], v["verdict"], v["fpCondition"], v["overstated"]) for v in out],
                         [("J001", "TP", None, False), ("J002", "FP", "reachability", True), ("P001", "U", None, False)])
        self.assertEqual(out[0]["reason"], "a/B.java:10 runs on the @Async pool")

    def test_overstated_first_word_and_note(self):
        for value, flag, note in [("Sí", True, None), ("No", False, None), ("No — la referencia se descarta", False, "No — la referencia se descarta")]:
            out = review_sheet.parse_sheet(self.filled(J002=("FP", "context", "r.py:1", value)), self.IDS)[1]
            self.assertEqual((out["overstated"], out["overstated_note"]), (flag, note), value)
        for value in ("Si", "no", "No, x", "No - x", "No —", "Quizá"):
            with self.assertRaises(ValueError, msg=value) as cm:
                review_sheet.parse_sheet(self.filled(J002=("FP", "context", "r.py:1", value)), self.IDS)
            self.assertIn("J002: Overstated", str(cm.exception))

    def test_fails_on_missing_or_invalid(self):
        for override, expected in [({"J002": ("", "—", "r.py:1", "No")}, "J002: verdict missing"),
                                   ({"J002": ("tp", "—", "r.py:1", "No")}, "J002: verdict 'tp' is not TP, FP or U"),
                                   ({"J002": ("FP", "", "r.py:1", "No")}, "J002: an FP needs its FP condition"),
                                   ({"J002": ("FP", "scope", "r.py:1", "No")}, "J002: an FP needs its FP condition"),
                                   ({"J002": ("TP", "context", "r.py:1", "No")}, "J002: FP condition 'context' on a TP"),
                                   ({"J002": ("TP", "—", "", "No")}, "J002: reason missing"),
                                   ({"J002": ("TP", "—", "runs on the pool", "No")}, "J002: reason cites no file:line"),
                                   ({"J002": ("TP", "—", "r.py:1", "")}, "J002: Overstated missing")]:
            with self.assertRaises(ValueError) as cm:
                review_sheet.parse_sheet(self.filled(**override), self.IDS)
            self.assertIn(expected, str(cm.exception))
        with self.assertRaises(ValueError):
            review_sheet.parse_sheet(self.filled(), ["J001", "J002"])  # an ID too many
        with self.assertRaises(ValueError):
            review_sheet.parse_sheet(review_sheet.render_sheet(self.IDS), self.IDS)  # empty sheet

    def test_sheet_ids_every_review_set_id_shuffled_with_fixed_seed(self):
        import random
        ids = [f"J{n:03d}" for n in range(1, 60)] + [f"P{n:03d}" for n in range(1, 101)]
        expected = list(ids)
        random.Random(20261204).shuffle(expected)
        self.assertEqual(review_sheet.sheet_ids(ids), expected)
        self.assertEqual(sorted(review_sheet.sheet_ids(ids)), sorted(ids))
        self.assertEqual(review_sheet.SEED_SHEET, 20261204)


class AICompare(unittest.TestCase):
    IDS = ["J001", "J002", "P001", "P002"]

    @staticmethod
    def out(verdicts):
        return {"entries": [{"id": i, "verdict": v, "valid": v is not None} for i, v in verdicts.items()]}

    def test_ai_verdicts_invalid_is_none_and_ids_must_match(self):
        got = ai_compare.ai_verdicts(self.out({"J001": "TP", "J002": None, "P001": "FP", "P002": "U"}), self.IDS)
        self.assertEqual(got, {"J001": "TP", "J002": None, "P001": "FP", "P002": "U"})
        with self.assertRaises(ValueError):
            ai_compare.ai_verdicts(self.out({"J001": "TP"}), self.IDS)

    def test_compare_invalid_counts_as_disagreement_and_threshold_is_informative(self):
        ai = {"J001": "TP", "J002": None, "P001": "FP", "P002": "U"}
        joaquin = {"J001": "TP", "J002": "TP", "P001": "FP", "P002": "TP"}
        c = ai_compare.compare(ai, joaquin, self.IDS)
        self.assertEqual((c["java"]["agree"], c["java"]["invalid"], c["java"]["disagreeing"]), (1, ["J002"], ["J002"]))
        self.assertEqual((c["all"]["n"], c["all"]["agree"], c["all"]["rate"]), (4, 2, 0.5))
        self.assertEqual(c["all"]["rateCI95"], ev.wilson(2, 4))
        self.assertFalse(c["all"]["meetsInformativeThreshold"])
        same = ai_compare.compare(joaquin, joaquin, self.IDS)
        self.assertTrue(same["all"]["meetsInformativeThreshold"])
        self.assertEqual(same["all"]["cohenKappa"], 1.0)
        self.assertEqual(ai_compare.THRESHOLD, 0.95)

    def test_render_says_it_never_decides(self):
        joaquin = {"J001": "TP", "J002": "TP", "P001": "FP", "P002": "TP"}
        md = ai_compare.render({"A": ai_compare.compare(joaquin, joaquin, self.IDS)})
        self.assertIn("never decides", md)
        self.assertIn("does **not** make the AI review a measurement method", md)

    def test_seal_refuses_inside_repo_and_after_the_sheet(self):
        with self.assertRaises(SystemExit) as cm:
            ai_compare.main(["seal", str(ai_compare.DIR / "x")])
        self.assertIn("inside the repository", str(cm.exception))
        with self.assertRaises(SystemExit):
            ai_compare.main(["peek", "/tmp/x"])


if __name__ == "__main__":
    unittest.main()
