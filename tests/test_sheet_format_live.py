"""Live test that creates a TEST_SHEET in Google Sheets to verify column alignment.
Runs against real Google Sheets API - requires valid credentials.

Run with:  pytest tests/test_sheet_format_live.py -m slow -s
"""
import os
import pytest
from src.sheets_handler import get_sheets_handler, FULL_HEADERS, FORMULA_STEFAN, TOTAL_ROW_TINE


@pytest.mark.slow
def test_new_sheet_columns_are_correct():
    """Verify _format_new_worksheet + append_row place data in correct columns.
    Creates TEST_SHEET, formats it, appends samples, verifies every cell
    position, then cleans up."""
    if not os.environ.get("GOOGLE_SHEETS_CREDS_FILE") or \
       not os.path.exists(os.environ.get("GOOGLE_SHEETS_CREDS_FILE", "")):
        pytest.skip("GOOGLE_SHEETS_CREDS_FILE not set or not found — skipping live test")

    from src.config import GOOGLE_SHEET_NAME

    h = get_sheets_handler()
    spreadsheet = h.client.open(GOOGLE_SHEET_NAME)

    # Clean existing test sheet
    for ws in spreadsheet.worksheets():
        if ws.title == "TEST_SHEET":
            spreadsheet.del_worksheet(ws)

    ws = spreadsheet.add_worksheet(title="TEST_SHEET", rows=100, cols=26)

    try:
        # Step 1: format exactly like _format_new_worksheet
        ws.append_row(FULL_HEADERS + [FORMULA_STEFAN], value_input_option="USER_ENTERED")
        ws.append_row(TOTAL_ROW_TINE, value_input_option="USER_ENTERED")

        # Step 2: add sample expenses
        expenses = [
            ["2026-07-10", "Coffee", 150.0, "Stefan"],
            ["2026-07-10", "Groceries", 850.0, "Maria"],
            ["2026-07-10", "Gas", 500.0, "Stefan"],
        ]
        for e in expenses:
            ws.append_row(e, value_input_option="USER_ENTERED")

        # Step 3: verify header row (columns A-F)
        r1 = {c.col: c.value for c in ws.range("A1:F1")}
        assert r1[1] == "Date"
        assert r1[2] == "Description"
        assert r1[3] == "Amount"
        assert r1[4] == "Paid By"
        assert r1[5] == "Total Stefan Paid"
        assert r1[6] in ("650", "650.0"), f"F1 (Stefan total) expected 650, got '{r1[6]}'"

        # Step 4: verify Maria totals row (columns E-F)
        r2 = {c.col: c.value for c in ws.range("A2:F2")}
        assert r2[5] == "Total Maria Paid:"
        assert r2[6] in ("0", "0.0"), f"F2 (Maria total) expected 0, got '{r2[6]}'"

        # Step 5: each expense in correct columns A-D
        for i, (exp_date, exp_item, exp_amount, exp_paid_by) in enumerate(expenses):
            row_num = i + 3
            cells = {c.col: c.value for c in ws.range(f"A{row_num}:D{row_num}")}
            assert cells[1] == exp_date, f"Row {row_num} A: expected '{exp_date}', got '{cells[1]}'"
            assert cells[2] == exp_item, f"Row {row_num} B: expected '{exp_item}', got '{cells[2]}'"
            assert cells[3] == str(exp_amount), f"Row {row_num} C: expected '{exp_amount}', got '{cells[3]}'"
            assert cells[4] == exp_paid_by, f"Row {row_num} D: expected '{exp_paid_by}', got '{cells[4]}'"

        # Step 6: verify columns K-N have NO data (old bug location)
        for c in ws.range("K3:N5"):
            assert c.value == "", f"Found data in wrong column {c.address}: '{c.value}'"

    finally:
        spreadsheet.del_worksheet(ws)
