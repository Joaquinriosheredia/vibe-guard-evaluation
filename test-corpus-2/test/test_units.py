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
import review_ab  # noqa: E402
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


def ab_inputs(rs, verdict_of, dis=(), audit=(), joaquin_of=None, over_a=None, over_b=None):
    """A and B agree on verdict_of(f) except on `dis` (B flips TP<->FP); Joaquín reviews dis + audit."""
    a, b = {}, {}
    for f in rs["findings"]:
        i, v = f["id"], verdict_of(f)
        a[i] = {"verdict": v, "overstated": bool(over_a and i in over_a)}
        b[i] = {"verdict": ({"TP": "FP", "FP": "TP", "U": "TP"}[v] if i in dis else v), "overstated": bool(over_b and i in over_b)}
    joaquin_of = joaquin_of or (lambda i: a[i]["verdict"])
    joaquin = {i: {"verdict": joaquin_of(i), "overstated": False} for i in list(dis) + list(audit)}
    return a, b, joaquin


AUDIT = ["J001", "J002", "J003", "J004", "J005", "J006", "J007"] + [f"P{n:03d}" for n in range(1, 14)]


class Evaluate(unittest.TestCase):
    def run_eval(self, rs, corpora, reports, *args, **kw):
        final, review = ev.final_verdicts(rs["findings"], *ab_inputs(rs, *args, **kw), kw.get("dis", ()), kw.get("audit", AUDIT))
        return ev.evaluate(rs, corpora, reports, final, review), final, review

    def test_joaquin_must_cover_exactly_the_reviewed_ids(self):
        rs, _, _ = synthetic()
        a, b, joaquin = ab_inputs(rs, lambda f: "TP", dis=["P100"], audit=AUDIT)
        del joaquin["P100"]
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], a, b, joaquin, ["P100"], AUDIT)
        a, b, joaquin = ab_inputs(rs, lambda f: "TP", dis=["P100"], audit=AUDIT)
        joaquin["P099"] = {"verdict": "TP", "overstated": False}
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], a, b, joaquin, ["P100"], AUDIT)

    def test_unreviewed_disagreement_is_refused(self):
        rs, _, _ = synthetic()
        a, b, joaquin = ab_inputs(rs, lambda f: "TP", dis=["P100"], audit=AUDIT)
        with self.assertRaises(SystemExit):
            ev.final_verdicts(rs["findings"], a, b, {i: joaquin[i] for i in AUDIT}, [], AUDIT)

    def test_final_is_joaquin_where_reviewed_else_a_equals_b(self):
        rs, _, _ = synthetic()
        a, b, joaquin = ab_inputs(rs, lambda f: "TP", dis=["P100"], audit=AUDIT, joaquin_of=lambda i: "U" if i == "P100" else "TP")
        final, review = ev.final_verdicts(rs["findings"], a, b, joaquin, ["P100"], AUDIT)
        self.assertEqual((final["P100"]["verdict"], final["P100"]["source"]), ("U", "Joaquín"))
        self.assertEqual((final["P050"]["verdict"], final["P050"]["source"]), ("TP", "A=B"))
        self.assertEqual(review["disagreements"], ["P100"])
        self.assertEqual(review["agreementAB"]["n"], 150)

    def test_overstated_disputed_is_yes_and_joaquin_decides_where_reviewed(self):
        rs, _, _ = synthetic()
        a, b, joaquin = ab_inputs(rs, lambda f: "TP", audit=AUDIT, over_a={"P050", "P051", "P001"}, over_b={"P051"})
        final, review = ev.final_verdicts(rs["findings"], a, b, joaquin, [], AUDIT)
        self.assertTrue(final["P050"]["overstated"])   # A yes, B no -> yes
        self.assertTrue(final["P051"]["overstated"])   # both yes
        self.assertFalse(final["P052"]["overstated"])  # both no
        self.assertFalse(final["P001"]["overstated"])  # in the audit: Joaquín said no
        self.assertEqual(review["overstatedDisputedSetToYes"], 2)  # P050 and P001

    def test_audit_two_changes_reliable_three_not_met_in_both_languages(self):
        rs, corpora, reports = synthetic()
        for changed, reliable in ((["J001", "P001"], True), (["J001", "P001", "P002"], False)):
            m, _, review = self.run_eval(rs, corpora, reports, lambda f: "TP", audit=AUDIT, joaquin_of=lambda i: "FP" if i in changed else "TP")
            au = review["audit"]
            self.assertEqual((au["n"], au["changed"], au["reliable"]), (20, len(changed), reliable))
            self.assertEqual((au["byLanguage"]["java"]["n"], au["byLanguage"]["java"]["changed"]), (7, 1))
            self.assertEqual((au["byLanguage"]["python"]["n"], au["byLanguage"]["python"]["changed"]), (13, len(changed) - 1))
            self.assertEqual(au["rateCI95"], ev.wilson(len(changed), 20))
            for lang in ("java", "python"):
                c1 = m["languages"][lang]["criterion1"]
                self.assertEqual(c1["status"], "MET" if reliable else "NOT MET")
                self.assertEqual(any("NOT RELIABLE" in r for r in c1["reasons"]), not reliable)
            self.assertIn("NOT RELIABLE" if not reliable else "**RELIABLE**", ev.render(m))

    def test_languages_are_separate(self):
        rs, corpora, reports = synthetic()
        m, _, _ = self.run_eval(rs, corpora, reports, lambda f: "TP" if f["language"] == "java" else ("TP" if int(f["id"][1:]) <= 80 else "FP"), audit=AUDIT)
        self.assertEqual(m["languages"]["java"]["criterion1"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["criterion1"]["status"], "NOT MET")  # 0.80
        self.assertEqual(m["languages"]["python"]["fpPer1000"]["primary"], 4.0)  # 20/100 × 20
        self.assertEqual(m["languages"]["python"]["criterion2"]["status"], "MET")
        self.assertEqual(m["languages"]["python"]["volume"]["per1000"]["warning"], 0.2)
        self.assertIn("does **not** show with 95 % confidence", ev.render(m))

    def test_java_short_of_the_sample_is_not_met(self):
        rs, corpora, reports = synthetic(n_java=30)
        m, _, _ = self.run_eval(rs, corpora, reports, lambda f: "TP", audit=AUDIT)
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

    def filled(self, **override):
        rows = {"J001": ("TP", "a/B.java:10 runs on the @Async pool", "No"),
                "J002": ("FP", "b/C.java:3 only called from tests", "Sí"),
                "P001": ("U", "x.py:5 caller outside the repository", "no")}
        rows.update(override)
        text = review_sheet.render_sheet(self.IDS)
        for i, (v, r, o) in rows.items():
            text = text.replace(f"## {i}\n\n- Card: [cards/{i}.md](cards/{i}.md)\n- Verdict: \n- Reason (file:line): \n- Overstated: ",
                                f"## {i}\n\n- Card: [cards/{i}.md](cards/{i}.md)\n- Verdict: {v}\n- Reason (file:line): {r}\n- Overstated: {o}")
        return text

    def test_sheet_has_only_id_card_and_empty_fields(self):
        text = review_sheet.render_sheet(self.IDS)
        block = text.split("## J001\n", 1)[1].split("## J002", 1)[0]
        self.assertEqual(block, "\n- Card: [cards/J001.md](cards/J001.md)\n- Verdict: \n- Reason (file:line): \n- Overstated: \n\n")

    def test_complete_sheet_converts(self):
        out = review_sheet.parse_sheet(self.filled(), self.IDS)
        self.assertEqual([(v["id"], v["verdict"], v["overstated"]) for v in out], [("J001", "TP", False), ("J002", "FP", True), ("P001", "U", False)])
        self.assertEqual(out[0]["reason"], "a/B.java:10 runs on the @Async pool")

    def test_fails_on_missing_or_invalid(self):
        for override, expected in [({"J002": ("", "r", "No")}, "J002: verdict missing"),
                                   ({"J002": ("tp", "r", "No")}, "J002: verdict 'tp' is not TP, FP or U"),
                                   ({"J002": ("TP", "", "No")}, "J002: reason missing"),
                                   ({"J002": ("TP", "r", "maybe")}, "J002: Overstated 'maybe' is not Sí or No"),
                                   ({"J002": ("TP", "r", "")}, "J002: Overstated missing")]:
            with self.assertRaises(ValueError) as cm:
                review_sheet.parse_sheet(self.filled(**override), self.IDS)
            self.assertIn(expected, str(cm.exception))
        with self.assertRaises(ValueError):
            review_sheet.parse_sheet(self.filled(), ["J001", "J002"])  # an ID too many
        with self.assertRaises(ValueError):
            review_sheet.parse_sheet(review_sheet.render_sheet(self.IDS), self.IDS)  # empty sheet

    def test_committed_sheet_and_guide(self):
        tc2 = Path(__file__).resolve().parent.parent
        ids = [f["id"] for f in __import__("json").loads((tc2 / "review-set.json").read_text())["findings"]]
        dis, audit = review_sheet.ab_lists((tc2 / "REVIEW-AB.md").read_text())
        self.assertEqual((len(dis), len(audit), len(set(dis) | set(audit))), (7, 20, 27))
        self.assertEqual((tc2 / "REVIEW-SHEET.md").read_text(), review_sheet.render_sheet(review_sheet.sheet_ids(ids, dis, audit)) + "\n")
        prereg = (tc2 / "PREREGISTRATION.md").read_text()
        guide = (tc2 / "REVIEW-GUIDE.md").read_text()
        verdicts = prereg[prereg.index("## Verdicts (the rules"):prereg.index("## Reviewers, cards and blindness")].rstrip("\n")
        assistance = prereg[prereg.index("**Assistance during the review:**"):prereg.index("**Known limit of the literal search:**")].rstrip("\n")
        self.assertIn(verdicts, guide)
        self.assertIn(assistance, guide)

    def test_sheet_ids_shuffled_with_fixed_seed_and_no_group_labels(self):
        import random
        ids = [f"J{n:03d}" for n in range(1, 30)] + [f"P{n:03d}" for n in range(1, 60)]
        dis, audit = ["J002", "P010"], ["J005", "P003", "P040"]
        expected = ["J002", "J005", "P003", "P010", "P040"]
        random.Random(20261026).shuffle(expected)
        self.assertEqual(review_sheet.sheet_ids(ids, dis, audit), expected)
        text = review_sheet.render_sheet(expected).lower()
        for word in ("disagree", "audit", "desacuerdo", "auditor"):
            self.assertNotIn(word, text)

    def test_ab_lists_parses_review_ab(self):
        md = "# x\n\n| a |\n\n## Disagreements (2): x\n\n- [J001](cards/J001.md)\n- [P072](cards/P072.md)\n\n## Audit sample (1 of x)\n\n- [P002](cards/P002.md)\n"
        self.assertEqual(review_sheet.ab_lists(md), (["J001", "P072"], ["P002"]))


class ReviewAB(unittest.TestCase):
    IDS = ["J001", "J002", "P001", "P002"]

    @staticmethod
    def v(i, verdict, reason="x.py:1 evidence", over=False):
        return {"id": i, "verdict": verdict, "reason": reason, "overstated": over}

    def test_merge_batches_orders_and_validates(self):
        out = review_ab.merge_batches([{"batch": 2, "verdicts": [self.v("P002", "U"), self.v("P001", "FP")]},
                                       {"batch": 1, "verdicts": [self.v("J001", "TP"), self.v("J002", "FP")]}], self.IDS)
        self.assertEqual([v["id"] for v in out], self.IDS)
        for bad, expected in [([self.v("J001", "TP"), self.v("J001", "TP")], "J001: appears twice"),
                              ([self.v("J001", "TP")], "do not cover exactly"),
                              ([self.v("J001", "tp"), self.v("J002", "FP"), self.v("P001", "U"), self.v("P002", "U")], "J001: verdict is not TP, FP or U"),
                              ([self.v("J001", "TP", " "), self.v("J002", "FP"), self.v("P001", "U"), self.v("P002", "U")], "J001: reason missing"),
                              ([self.v("J001", "TP", over="No"), self.v("J002", "FP"), self.v("P001", "U"), self.v("P002", "U")], "J001: overstated is not true/false")]:
            with self.assertRaises(ValueError) as cm:
                review_ab.merge_batches([{"verdicts": bad}], self.IDS)
            self.assertIn(expected, str(cm.exception))

    def test_compare_is_on_the_verdict_only_and_per_language(self):
        a = [self.v("J001", "TP"), self.v("J002", "FP"), self.v("P001", "U"), self.v("P002", "TP", over=True)]
        b = [self.v("J001", "TP", "other.py:2"), self.v("J002", "TP"), self.v("P001", "U"), self.v("P002", "TP", over=False)]
        c = review_ab.compare(a, b, self.IDS)
        self.assertEqual((c["java"]["agree"], c["java"]["disagreeing"]), (1, ["J002"]))
        self.assertEqual((c["python"]["agree"], c["python"]["disagree"]), (2, 0))
        self.assertEqual((c["all"]["n"], c["all"]["disagreeing"]), (4, ["J002"]))

    def test_audit_sample_seed_size_and_order(self):
        agreeing = [f"P{n:03d}" for n in range(1, 60)]
        s = review_ab.audit_sample(agreeing)
        self.assertEqual(len(s), 20)
        self.assertEqual(s, [i for i in agreeing if i in s])
        import random
        self.assertEqual(set(s), set(random.Random(20261025).sample(agreeing, 20)))
        with self.assertRaises(ValueError):
            review_ab.audit_sample(agreeing[:19])

    def test_render_shows_ids_and_counts_never_verdicts(self):
        a = [self.v("J001", "TP"), self.v("J002", "FP"), self.v("P001", "U"), self.v("P002", "TP")]
        b = [self.v("J001", "TP"), self.v("J002", "TP"), self.v("P001", "U"), self.v("P002", "TP")]
        md = review_ab.render(review_ab.compare(a, b, self.IDS), ["J001"])
        self.assertIn("- [J002](cards/J002.md)", md)
        for word in ("TP |", "| TP", "FP |", "| FP", " U |", "TP\n", "FP\n"):
            self.assertNotIn(word, md)


if __name__ == "__main__":
    unittest.main()
