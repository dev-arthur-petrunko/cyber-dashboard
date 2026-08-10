"""Тесты для app/scoring.py — власна оцінка ризику та витягування vendor."""
from app.scoring import compute_local_score, extract_vendor


class TestComputeLocalScore:
    def test_returns_none_when_no_data(self):
        assert compute_local_score() is None

    def test_severity_base(self):
        assert compute_local_score(severity="Critical") == 9.0
        assert compute_local_score(severity="High") == 7.5
        assert compute_local_score(severity="Medium") == 5.0
        assert compute_local_score(severity="Low") == 2.0
        assert compute_local_score(severity="Unknown") == 4.0

    def test_unknown_severity_falls_back_to_4(self):
        assert compute_local_score(severity="Weird") == 4.0

    def test_maturity_bump(self):
        assert compute_local_score(severity="High", exploit_maturity="In the wild") == 7.5 + 1.2
        assert compute_local_score(severity="High", exploit_maturity="Weaponized") == 7.5 + 0.8
        assert compute_local_score(severity="High", exploit_maturity="PoC") == 7.5 + 0.5
        assert compute_local_score(severity="High", exploit_maturity="Unknown") == 7.5

    def test_epss_contribution_capped(self):
        assert compute_local_score(severity="Medium", epss_score=1.0) == 5.0 + 2.0
        assert compute_local_score(severity="Medium", epss_score=0.5) == 5.0 + 1.0
        # epss > 1.0 должен обрезаться до максимума
        assert compute_local_score(severity="Medium", epss_score=5.0) == 7.0

    def test_keyword_bump(self):
        assert (
            compute_local_score(severity="Medium", title="Ransomware attack on hospitals")
            == 5.0 + 0.6
        )
        assert (
            compute_local_score(severity="Medium", tags=["zero-day", "exploit"])
            == 5.0 + 0.6
        )
        assert compute_local_score(severity="Medium", title="Benign news") == 5.0

    def test_result_capped_at_10(self):
        score = compute_local_score(
            severity="Critical",
            exploit_maturity="In the wild",
            epss_score=1.0,
            title="critical ransomware zero-day exploit",
        )
        assert score == 10.0

    def test_score_rounded_to_one_decimal(self):
        score = compute_local_score(
            severity="High", exploit_maturity="PoC", epss_score=0.33
        )
        assert isinstance(score, float)
        assert score == round(score, 1)


class TestExtractVendor:
    def test_returns_none_for_empty_input(self):
        assert extract_vendor() is None

    def test_extracts_vendor_from_title(self):
        assert extract_vendor(title="Critical SharePoint RCE") == "Microsoft"

    def test_extracts_longest_match_first(self):
        # "palo alto" — підрядок "palo alto networks" → має взятися повний бренд
        assert (
            extract_vendor(title="Vulnerability in Palo Alto Networks PAN-OS")
            == "Palo Alto Networks"
        )

    def test_extracts_from_tags(self):
        assert extract_vendor(tags=["fortinet", "firewall"]) == "Fortinet"

    def test_vendor_keyword_requires_word_boundary(self):
        # "microsoftedge" не повинно матчитись як "microsoft"
        assert extract_vendor(title="microsoftedge exploit") is None

    def test_case_insensitive(self):
        assert extract_vendor(title="Critical WINDOWS kernel bug") == "Microsoft"

    def test_summary_used_when_title_empty(self):
        assert extract_vendor(summary="Apache httpd path traversal") == "Apache"
