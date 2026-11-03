"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

from crud.lexer import tokenize, TokenType as T


def test_regresi_keyword_campuran_huruf():
    # SPESIFIKASI 2.2: keyword tidak peka huruf besar/kecil, nilainya selalu huruf besar.
    toks = tokenize("Select x fRoM t")
    assert [(t.type, t.value) for t in toks[:4]] == [
        (T.KEYWORD, "SELECT"), (T.IDENT, "x"), (T.KEYWORD, "FROM"), (T.IDENT, "t")]


def test_kata_berawalan_keyword_tetap_ident():
    # 'selection' dan 'fromage' hanya DIAWALI keyword, jadi tetap IDENT.
    toks = tokenize("selection fromage")
    assert [(t.type, t.value) for t in toks[:2]] == [
        (T.IDENT, "selection"), (T.IDENT, "fromage")]