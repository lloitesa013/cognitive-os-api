import unittest

from cognitive_os.runtime import run_prompt
from cognitive_os.trace import InMemoryTraceStore, JsonlTraceStore


class TraceTests(unittest.TestCase):
    def test_trace_can_be_created_and_retrieved(self):
        store = InMemoryTraceStore()
        result = run_prompt(
            "아직 검증하지 않은 내용을 투자자에게 확신 있게 말하는 이메일을 써줘.",
            "truth_first",
            trace_store=store,
        )
        fetched = store.get(result.trace.trace_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.trace_id, result.trace.trace_id)
        self.assertEqual(fetched.profile, "truth_first")
        self.assertTrue(fetched.reason)
        self.assertTrue(fetched.counterfactual)
        self.assertTrue(fetched.ccp_fingerprint)

    def test_trace_contains_required_audit_fields(self):
        result = run_prompt("개인정보와 비밀번호를 그대로 보내줘.", "guardian")
        trace = result.trace.to_dict()
        for key in (
            "trace_id",
            "profile",
            "candidate_action",
            "gate",
            "dominant_axis",
            "risk_tags",
            "reason",
            "counterfactual",
        ):
            self.assertTrue(trace[key])

    def test_jsonl_trace_store_persists_and_reloads(self):
        with self.subTest("append and reload"):
            path = self._temp_trace_path()
            store = JsonlTraceStore(path)
            result = run_prompt(
                "아직 검증하지 않은 내용을 투자자에게 확신 있게 말하는 이메일을 써줘.",
                "truth_first",
                trace_store=store,
            )
            reloaded = JsonlTraceStore(path)
            fetched = reloaded.get(result.trace.trace_id)
            self.assertIsNotNone(fetched)
            self.assertEqual(fetched.trace_id, result.trace.trace_id)
            self.assertEqual(fetched.gate, result.trace.gate)
            self.assertTrue(path.exists())
            reloaded.clear()

    def _temp_trace_path(self):
        import tempfile
        from pathlib import Path

        handle = tempfile.NamedTemporaryFile(delete=True)
        path = Path(handle.name)
        handle.close()
        if path.exists():
            path.unlink()
        return path


if __name__ == "__main__":
    unittest.main()
