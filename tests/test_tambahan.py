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
    cols, diags = _resolve("SELECT (SELECT x FROM a, b) FROM pelanggan")
    assert cols[0].resolved is None


def test_kolom_tanpa_qualifier_dua_tabel_ambigu():
    cols, diags = _resolve("SELECT nama FROM pelanggan p, pesanan o")
    # 1. Pastikan resolved dari kolom tetap None (karena ambigu)
    assert cols[0].resolved is None
    # 2. Pastikan muncul warning bahwa kolom ambigu tanpa skema
    assert len(diags) == 1
    assert diags[0].level == "warning"
    assert "ambigu tanpa skema" in diags[0].message

def test_regresi_update_subquery_selalu_read():
    # SPESIFIKASI bagian 5:
    # "Membaca tabel lewat subquery selalu R, apa pun jenis statement luarnya."
    # Pada UPDATE, tabel target bernilai 'U', tetapi tabel di dalam subquery
    # (baik pada klausa SET maupun WHERE) wajib bernilai 'R'.
    sql = """
    UPDATE pelanggan
    SET skor = (SELECT skor_awal FROM profil WHERE id = pelanggan.id)
    WHERE id IN (SELECT pelanggan_id FROM pesanan);
    """
    script = parse_sql(sql)
    assert script.errors == [], script.errors
    assert len(script.statements) == 1
    usage = analyze_statement(script.statements[0])
    assert usage == {"pelanggan": {"U"}, "pesanan": {"R"}, "profil": {"R"}}


def test_regresi_operator_tidak_sama_dengan():
    # SPESIFIKASI 2.5: Operator maximal munch.
    # '<>' harus dibaca sebagai satu kesatuan token OP, bukan terpisah '<' lalu '>'.
    toks = tokenize("a <> b")
    assert toks[1].type == T.OP
    assert toks[1].value == "<>"


def test_regresi_scope_delete_tidak_bocor():
    # SPESIFIKASI 4.5: Setiap statement berdiri sendiri.
    # Setelah DELETE selesai di-resolve, scope harus bersih (None),
    # dan alias dari DELETE tidak boleh terlihat oleh statement berikutnya.
    sql = """
    DELETE FROM pelanggan p WHERE p.id = 1;
    SELECT p.nama FROM pesanan o;
    """
    script = parse_sql(sql)
    resolver = Resolver()
    diags = resolver.resolve_script(script)

    # 1. Pastikan tidak ada scope yang tersisa setelah resolusi
    assert resolver.scope is None

    # 2. Statement kedua harus error karena alias 'p' milik statement DELETE sebelumnya
    assert len(diags) == 1
    assert diags[0].level == "error"
    assert "alias 'p' tidak terdefinisi" in diags[0].message


def test_regresi_panic_mode_error_recovery():
    # SPESIFIKASI bagian 6: Error recovery (panic mode).
    # Setelah error sintaks, parser harus membuang token sampai ';' berikutnya,
    # dan statement valid setelahnya tetap harus berhasil diproses.
    sql = """
    SELECT FROM;
    SELECT id FROM pelanggan;
    """
    script = parse_sql(sql)

    # 1. Statement rusak menghasilkan tepat satu ParseError
    assert len(script.errors) == 1

    # 2. Statement valid setelahnya tetap diproses (tidak boleh terbuang)
    assert len(script.statements) == 1
    assert script.statements[0].sources[0].name == "pelanggan"
