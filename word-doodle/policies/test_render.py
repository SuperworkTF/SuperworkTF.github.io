# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""Publisher regressions: uv run --no-project word-doodle/policies/test_render.py."""
import re
import sys
import unittest

sys.dont_write_bytecode = True
import render


class PolicyPublisherTests(unittest.TestCase):
    metadata = {"title": "개인정보처리방침", "public_url": "https://superworktf.github.io/word-doodle/privacy/"}
    source = "# 그려보카 개인정보처리방침\n시행일: 2026.09.09\n## 1. 처리 항목\n문의 처리 완료 후 즉시 삭제\n"
    archive = {"version": "2026-09-09", "notice": "문서 정비 전 방침입니다."}

    def test_current_navigation_and_canonical(self):
        html = render.page("privacy", self.source, self.metadata)
        self.assertIn('<link rel="canonical" href="'+self.metadata["public_url"]+'">', html)
        self.assertIn('href="../styles.css"', html)
        self.assertIn('href="../privacy/" aria-current="page"', html)
        self.assertIn('href="../../">전체 앱 안내', html)
        self.assertNotIn('class="archive-note"', html)

    def test_archive_navigation_and_canonical(self):
        html = render.page("privacy", self.source, self.metadata, archive=self.archive)
        self.assertIn('href="'+self.metadata["public_url"]+'2026-09-09/"', html)
        self.assertIn('href="../../styles.css"', html)
        self.assertIn('href="../../privacy/" aria-current="page"', html)
        self.assertIn('href="../../../">전체 앱 안내', html)
        self.assertIn('href="../../privacy/">현재 방침 보기', html)
        self.assertIn('— 정비 전 문서</title>', html)

    def test_archive_does_not_change_policy_body(self):
        current = render.page("privacy", self.source, self.metadata)
        archive = render.page("privacy", self.source, self.metadata, archive=self.archive)
        body = re.compile(r'<article.*?>(.*?)</article>', re.S)
        self.assertEqual(body.search(current).group(1), body.search(archive).group(1))

    def test_archive_notice_is_escaped(self):
        html = render.page("privacy", self.source, self.metadata, archive={**self.archive, "notice": "<script>alert(1)</script>"})
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_invalid_archive_path_rejected(self):
        with self.assertRaisesRegex(ValueError, "Invalid archive version"):
            render.page("privacy", self.source, self.metadata, archive={**self.archive, "version": "../../outside"})

    def test_private_drafting_material_rejected(self):
        for marker in ("[내부 확인 B1]", "{{EFFECTIVE_DATE}}", r"\{\{APP_NAME\}\}", "<ancestor-path>"):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "private drafting"):
                render.page("privacy", self.source+marker, self.metadata)

    def test_public_source_is_accepted(self):
        render.assert_public_source(self.source)

    def test_tables_are_accessible_and_preserve_cells_and_links(self):
        source = '<table header-row="true">\n<tr>\n<td>항목</td>\n<td>안내</td>\n</tr>\n<tr>\n<td>문의</td>\n<td>[처리 안내](https://example.com/) 즉시 삭제</td>\n</tr>\n</table>'
        body = render.render_body(source)
        render.assert_fidelity(source, body)
        self.assertIn('<th scope="col">항목</th>', body)
        self.assertIn('tabindex="0"', body)
        self.assertIn('href="https://example.com/"', body)

    def test_fidelity_rejects_missing_text(self):
        with self.assertRaisesRegex(ValueError, "Policy text mismatch"):
            render.assert_fidelity("즉시 삭제", "<p>삭제</p>")

    def test_fidelity_rejects_changed_link(self):
        with self.assertRaisesRegex(ValueError, "Policy link mismatch"):
            render.assert_fidelity("[안내](https://example.com/)", '<p><a href="https://example.org/">안내</a></p>')


if __name__ == "__main__":
    unittest.main()
