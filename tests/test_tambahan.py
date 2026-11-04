"""Test tambahan buatan kelompok.

Isi dengan:
1. Satu test regresi untuk setiap bug yang kalian perbaiki (gagal sebelum perbaikan,
   lulus sesudahnya). Beri nama yang menjelaskan bug-nya.
2. Lima test kasus tepi, masing-masing dengan komentar singkat mengapa kasus itu berisiko.
"""

import pytest

from crud.analyzer import analyze_statement
from crud.lexer import LexError, TokenType as T, tokenize
from crud.parser import parse_sql
from crud.resolver import Resolver
from crud import ast_nodes as ast


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

def test_komentar_blok_tidak_ditutup_harus_error():
    # SPESIFIKASI 2.3: Komentar blok yang tidak ditutup adalah LexError.
    # Posisi error harus menunjuk ke baris dan kolom tempat '/*' dimulai.
    with pytest.raises(LexError) as exc_info:
        tokenize("SELECT 1;\n/* komentar tidak ditutup\nSELECT 2;")
    assert exc_info.value.line == 2
    assert exc_info.value.col == 1
    assert "tidak ditutup" in str(exc_info.value).lower()


def test_kasus_tepi_komentar_blok_berisi_bintang():
    # SPESIFIKASI 2.3: Komentar blok boleh berisi '*',
    # Lexer harus tetap mengabaikannya sampai menemukan penutup '*/'.
    sql = "/* rumus: 2 * 3 = 6 *** HEADER *** */ SELECT * FROM t"
    toks = tokenize(sql)
    values = [t.value for t in toks if t.type != T.EOF]
    assert values == ["SELECT", "*", "FROM", "t"]


def test_regresi_crud_insert_into_select():
    # SPESIFIKASI bagian 5:
    # INSERT ... SELECT -> tabel target bertipe 'C', sedangkan tabel sumber bertipe 'R'.
    sql = "INSERT INTO arsip (id, total) SELECT id, total FROM pesanan WHERE total > 10;"
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    usage = analyze_statement(script.statements[0])
    assert usage == {"arsip": {"C"}, "pesanan": {"R"}}


def _resolve(sql):
    script = parse_sql(sql)
    diags = Resolver().resolve_script(script)
    cols = [n for n in ast.iter_nodes(script) if isinstance(n, ast.ColumnRef)]
    return cols, diags

def test_kolom_tanpa_qualifier_satu_tabel_tambahan():
    cols, diags = _resolve("SELECT nama FROM pelanggan")
    assert cols[0].resolved == "pelanggan"

def test_kolom_tanpa_qualifier_scope_luar_tidak_terlihat():
    # Kolom 'x' di subquery tidak boleh melihat tabel 'pelanggan' dari scope luar
    cols, diags = _resolve("SELECT (SELECT x) FROM pelanggan")
    assert cols[0].resolved is None


def test_kolom_tanpa_qualifier_dua_tabel_ambigu():
    cols, diags = _resolve("SELECT nama FROM pelanggan p, pesanan o")
    # 1. Pastikan resolved dari kolom tetap None (karena ambigu)
    assert cols[0].resolved is None
    # 2. Pastikan muncul warning bahwa kolom ambigu tanpa skema
    assert len(diags) == 1
    assert diags[0].level == "warning"
    assert "ambigu tanpa skema" in diags[0].message