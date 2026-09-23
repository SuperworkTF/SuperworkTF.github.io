# /// script
# requires-python = ">=3.10"
# dependencies = ["markdown-it-py==3.0.0"]
# ///
"""배포기 회귀 검사: uv run --no-project tools/test_render.py

네 앱이 함께 쓰는 렌더러를 문다(`tools/render-policies.py`). 앱 이름이 이 파일에 박혀
있는 곳은 예시 문자열뿐이고, 무는 것은 **모양**이다."""
import re
import sys
import unittest

sys.dont_write_bytecode = True
import importlib.util
import pathlib

_spec = importlib.util.spec_from_file_location(
    "render_policies", pathlib.Path(__file__).with_name("render-policies.py")
)
render = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(render)


class PolicyPublisherTests(unittest.TestCase):
    app = {"dir": "word-doodle", "brand": "그려보카", "theme_color": "#f7f4eb"}
    metadata = {"title": "개인정보처리방침", "public_url": "https://superwork.ai.kr/word-doodle/privacy/"}
    source = "# 그려보카 개인정보처리방침\n시행일: 2026.09.09\n## 1. 처리 항목\n문의 처리 완료 후 즉시 삭제\n"
    # 판 하나 = 출력 한 장. 정본 자리는 `path` 가 문서 이름과 같고, 지난 판은 그 아래 날짜다.
    base = {"path": "privacy", "source": "privacy"}
    archive = {"path": "privacy/2026-09-09", "source": "privacy-2026-09-09",
               "notice": "문서 정비 전 방침입니다."}

    def test_current_navigation_and_canonical(self):
        html = render.page("privacy", self.source, self.metadata, self.app, edition=self.base)
        self.assertIn('<link rel="canonical" href="'+self.metadata["public_url"]+'">', html)
        self.assertIn('href="../styles.css"', html)
        self.assertIn('href="../privacy/" aria-current="page"', html)
        self.assertIn('href="../../">전체 앱 안내', html)
        self.assertNotIn('class="archive-note"', html)

    def test_archive_navigation_and_canonical(self):
        html = render.page("privacy", self.source, self.metadata, self.app, edition=self.archive)
        self.assertIn('href="'+self.metadata["public_url"]+'2026-09-09/"', html)
        self.assertIn('href="../../styles.css"', html)
        self.assertIn('href="../../privacy/" aria-current="page"', html)
        self.assertIn('href="../../../">전체 앱 안내', html)
        self.assertIn('href="../../privacy/">현재 방침 보기', html)
        self.assertIn('— 정비 전 문서</title>', html)

    def test_archive_does_not_change_policy_body(self):
        current = render.page("privacy", self.source, self.metadata, self.app, edition=self.base)
        archive = render.page("privacy", self.source, self.metadata, self.app, edition=self.archive)
        body = re.compile(r'<article.*?>(.*?)</article>', re.S)
        self.assertEqual(body.search(current).group(1), body.search(archive).group(1))

    def test_archive_notice_is_escaped(self):
        html = render.page("privacy", self.source, self.metadata, self.app, edition={**self.archive, "notice": "<script>alert(1)</script>"})
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)

    def test_edition_path_outside_the_document_is_rejected(self):
        """자리 이름이 곧 디렉터리다. 거슬러 올라가는 자리를 허락하면 렌더러가 저장소 밖에 쓴다."""
        for path in ("privacy/../../outside", "privacy/무단", "../outside"):
            with self.subTest(path=path), self.assertRaises((ValueError, SystemExit)):
                render.editions_of("privacy", {"editions": [self.base, {**self.archive, "path": path}]})

    def test_edition_keeps_its_own_title(self):
        """**박제된 판의 제목을 고치지 않는다.** 짤랑 2026-09-04 판은 「개인정보 처리방침」
        (띄어씀)이고 2026-09-29 판은 「개인정보처리방침」이다 — 그날 게시된 이름이 그것이다.
        판 제목을 문서 칸의 것으로 덮으면 머리글 대조(`assert`)가 터지거나, 더 나쁘게는
        박제가 지금 이름으로 슬그머니 바뀐다."""
        spaced = {**self.archive, "title": "개인정보 처리방침"}
        html = render.page(
            "privacy", "# 그려보카 개인정보 처리방침\n## 1. 처리 항목\n즉시 삭제\n",
            self.metadata, self.app, edition=spaced)
        self.assertIn("<h1>그려보카 개인정보 처리방침</h1>", html)
        self.assertIn("<title>그려보카 개인정보 처리방침 — 정비 전 문서</title>", html)

    def test_two_editions_cannot_share_one_place(self):
        """같은 자리에 둘이 서면 나중 것이 앞 것을 덮는다 — 조용히 한 판이 사라진다."""
        with self.assertRaisesRegex(SystemExit, "같은 자리"):
            render.editions_of("privacy", {"editions": [self.base, dict(self.base)]})

    def test_first_edition_must_be_the_canonical_place(self):
        with self.assertRaisesRegex(SystemExit, "정본 자리"):
            render.editions_of("privacy", {"editions": [self.archive]})

    def test_private_drafting_material_rejected(self):
        for marker in ("[내부 확인 B1]", "{{EFFECTIVE_DATE}}", r"\{\{APP_NAME\}\}", "<ancestor-path>"):
            with self.subTest(marker=marker), self.assertRaisesRegex(ValueError, "private drafting"):
                render.page("privacy", self.source+marker, self.metadata, self.app, edition=self.base)

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


    def test_nav_lists_only_documents_the_app_publishes(self):
        html = render.page("privacy", self.source, self.metadata, self.app, edition=self.base,
                           kinds=("privacy", "account-deletion"))
        self.assertNotIn("terms/", html)
        self.assertIn('href="../account-deletion/">계정 삭제</a>', html)

    def test_kinds_follow_menu_order_and_reject_unknown(self):
        sources = {"account-deletion": {}, "privacy": {}}
        self.assertEqual(render.kinds_of("x", sources), ("privacy", "account-deletion"))
        with self.assertRaises(SystemExit):
            render.kinds_of("x", {"privacy": {}, "faq": {}})
        with self.assertRaises(SystemExit):
            render.kinds_of("x", {"terms": {}})

if __name__ == "__main__":
    unittest.main()
