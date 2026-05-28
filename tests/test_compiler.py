import unittest

from cognitive_os.compiler import compile_profile
from cognitive_os.schemas import CCP, FiveAnchors


class CompilerTests(unittest.TestCase):
    def test_builtin_profiles_have_expected_dominant_priorities(self):
        self.assertEqual(compile_profile("guardian").dominant_priority, "safety")
        self.assertEqual(compile_profile("truth_first").dominant_priority, "truth")
        self.assertEqual(compile_profile("progress_max").dominant_priority, "efficiency")

    def test_compile_is_stable_across_reload(self):
        ccp = compile_profile("truth_first")
        reloaded = CCP.from_dict(ccp.to_dict())
        self.assertEqual(ccp.fingerprint, reloaded.fingerprint)
        self.assertEqual(ccp.to_dict(), reloaded.to_dict())

    def test_custom_anchors_compile_to_machine_readable_ccp(self):
        anchors = FiveAnchors(
            profile_name="privacy_guard",
            desire="help while protecting private information",
            fear="leaking personal data or confidential secrets",
            goal="answer without exposing private data",
            priority="privacy",
            alternative="ask for consent or redact sensitive fields",
        )
        ccp = compile_profile(anchors)
        self.assertEqual(ccp.profile_name, "privacy_guard")
        self.assertEqual(ccp.dominant_priority, "privacy")
        self.assertIn("privacy_leakage", ccp.forbidden_modes)
        self.assertAlmostEqual(sum(ccp.drive_weights.values()), 1.0, places=3)


if __name__ == "__main__":
    unittest.main()
