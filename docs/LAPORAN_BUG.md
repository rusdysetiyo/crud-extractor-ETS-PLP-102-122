# Laporan Bug

Salin blok di bawah untuk setiap bug. Bagian **Akar masalah** wajib ditulis dengan kata-kata
sendiri dan memakai konsep dari *Crafting Interpreters* (sebutkan bab). Bagian ini diuji lisan.

---

## Bug 1: (judul singkat)

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input, output yang didapat, dan output yang diharapkan menurut SPESIFIKASI.md
(sebutkan bagiannya).

**Reproduksi minimal.** SQL terpendek yang memicu bug:

```sql

```

**Akar masalah.** Mengapa kode lama salah? Konsep apa yang dilanggar?

**Perbaikan.** File dan fungsi yang diubah, serta alasannya. Sebutkan juga perbaikan
alternatif yang kalian pertimbangkan dan alasan tidak memilihnya.

**Test regresi.** Nama test di `tests/test_tambahan.py` yang gagal sebelum perbaikan dan lulus
sesudahnya.

**Peran AI.** Apakah AI membantu menemukan atau memperbaiki bug ini? Bagaimana kalian
memverifikasinya?

---

## Bug 1: Normalisasi Keyword Huruf Kecil dan Campuran di Lexer

**Ditemukan oleh:** Gharin Fawwaz  **Diperbaiki oleh:** Gharin Fawwaz

**Gejala:** input SELECT id FROM t where x = 1, outputnya error parser. untuk otput yang di harapkan seharusnya tidak error dan sesuai SEPESIFIKASI 2.2

**Reproduksi minimal:**
```sql
Select x fRoM t
SELECT id FROM t where x = 1
```
**Akar masalah.** Kode lama membandingkan teks apa adanya (`text in KEYWORDS`), padahal `KEYWORDS` hanya berisi huruf besar. Python membedakan `"where"` dan `"WHERE"`, sehingga pencocokan gagal. Lexer tidak melaporkan error karena bagi lexer `where` sah sebagai nama (`IDENT`).

Error baru muncul di parser, bukan di lexer. Parser membaca `FROM t`, lalu menganggap `where` sebagai alias tabel `t`, karena grammar mengizinkan alias berupa `IDENT` setelah nama tabel. Setelah alias, parser mengharapkan `;` atau keyword lanjutan, tetapi menemukan `x`, sehingga error dilaporkan di sana.

Konsep ini ada di *Crafting Interpreters* Bab 4 bagian 4.7: scanner membaca satu kata utuh terlebih dahulu, baru kemudian memeriksa apakah kata itu reserved word. Alur di kode sudah mengikuti urutan itu dengan benar. yang salah adalah langkah pengecekannya, yang peka huruf besar/kecil dan tidak menormalisasi nilai. Hal ini melanggar SPESIFIKASI 2.2, yaitu keyword tidak peka huruf besar/kecil dan nilai token keyword selalu dinormalisasi ke huruf besar.

**Perbaikan.** Pada `crud/lexer.py`, fungsi `_word`, ada dua perubahan: pengecekan ke `KEYWORDS` memakai `text.upper()`, dan nilai token keyword disimpan dalam huruf besar. Alternatif yang dipertimbangkan: (a) mengubah isi `KEYWORDS` menjadi huruf kecil, ditolak karena melanggar spesifikasi nilai huruf besar dan merusak parser, sedangkan alternatif (b) mengubah seluruh teks SQL menjadi huruf besar sebelum di-lexing, ditolak karena merusak data dan posisi kolom.

**Test regresi.** 
test_regresi_keyword_campuran_huruf: gagal sebelum perbaikan (token IDENT), lulus sesudahnya.
test_kata_berawalan_keyword_tetap_ident: lulus sebelum dan sesudah. berfungsinya sebagai penjaga supaya perbaikan tidak berlebihan.

**Peran AI.** ya AI sangat membantuku menemukan bug ini, AI menujukan lokasi peyebab dan kode perbaikan, selain itu saya juga meminta AI untuk menjelaskan code dan juga akar masalah yang dasar teorinya kurang saya pahami, saya memverifikasinya hasilnya menggunakan pytest, pengecekan manual dengan python -c, dan membandingkan dengan spesifikasi 2.2.

## Bug 2: Resolusi Kolom Tanpa Qualifier Belum Diimplementasikan (TODO 2)

**Ditemukan oleh:** Gharin Fawwaz  **Diperbaiki oleh:** Gharin Fawwaz

**Gejala:** Ketika terdapat kolom tanpa qualifier pada scope yang memiliki lebih dari satu tabel, sistem gagal mendeteksi keambiguan tersebut. Output yang didapat: atribut resolved dibiarkan kosong dan tidak ada peringatan apa pun. Output yang diharapkan menurut SPESIFIKASI.md 4.3: sistem harus mengeluarkan warning

**Reproduksi minimal:**
SELECT nama FROM pelanggan p, pesanan o

**Akar masalah.**
Dalam buku Crafting Interpreters Bab 11: Resolving and Binding, sebuah resolver bertanggung jawab untuk mengikat  setiap variabel ke deklarasinya secara leksikal. Kode lama hanya menggunakan blok pass dan gagal menelusuri environment (scope) untuk melakukan binding statis pada kolom tersebut, sehingga interpreter kehilangan jejak asal usul kolom.

**Perbaikan.**
File yang diubah adalah crud/resolver.py pada fungsi _column. Perbaikan dilakukan dengan mengekstrak nilai dari self.scope.entries dan mengecek jumlah tabelnya. Jika tepat 1, resolve ke tabel tersebut; jika > 1, keluarkan warning ambigu; jika 0, keluarkan warning tidak ada tabel. Alternatif yang dipertimbangkan adalah membiarkan program menebak salah satu tabel secara acak saat ambigu, namun ditolak karena dapat menyebabkan silent error yang berbahaya pada matriks tabel.

**Test regresi.** test_kolom_tanpa_qualifier_dua_tabel_ambigu

**Peran AI.**
ya, AI membantu merumuskan logika percabangan untuk pengecekan entri pada scope serta menyusun fungsi pengujian.

---

## Bug 3: Komentar Blok (/* ... */) Belum Didukung di Lexer

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input kueri SQL yang memuat komentar blok `/* ... */` menghasilkan error leksikal `LexError: Baris X, kolom Y: komentar blok belum didukung`. 
Output yang diharapkan menurut SPESIFIKASI.md bagian 2.3 adalah komentar blok diabaikan dan tidak menghasilkan token sama sekali, 
serta jika tidak ditutup hingga akhir berkas harus melempar `LexError`.

**Reproduksi minimal.**

```sql
/* komentar */ SELECT 1;
```

**Akar masalah.**  Pada kode lama di `crud/lexer.py`, saat karakter `/*` terdeteksi, program hanya berisi komentar `TODO(T3)` 
dan langsung melempar `LexError("komentar blok belum didukung", line, col)`, belum memindai isi komentar hingga penutup `*/` seperti yang diharapkan SPESIFIKASI.md bagian 2.3.

**Perbaikan.** Pada file `crud/lexer.py`, di fungsi `_scan_token`, baris pelemparan error diganti dengan pemanggilan helper `self._block_comment(line, col)`. 
Fungsi ini memajukan pembacaan karakter menggunakan `_advance()`, mengabaikan karakter `*` biasa di dalam teks, melewati `*/` saat menemukannya dan berhenti, 
serta melempar `LexError("komentar blok tidak ditutup", line, col)` jika mencapai akhir input (`EOF`).  


**Test regresi.**
- `test_regresi_komentar_blok_tidak_ditutup_harus_error`
- `test_komentar_blok` (di `tests/test_lexer.py`)
- `test_kasus_tepi_komentar_blok_berisi_bintang`

**Peran AI.** (Isikan peran AI di sini)

---

## Bug 4: Sintaks INSERT INTO ... SELECT Belum Didukung di Parser

**Ditemukan oleh:** (nama) · **Diperbaiki oleh:** (nama)

**Gejala.** Input kueri SQL berupa `INSERT INTO ... SELECT ...` menghasilkan error sintaks `ParseError: Baris X, kolom Y: INSERT ... SELECT belum didukung, ditemukan 'SELECT'`. Output yang diharapkan menurut SPESIFIKASI.md bagian 3 dan bagian 5 adalah kueri berhasil di-parse ke dalam node `ast.Insert` dengan subquery `query` yang valid, serta diekstrak matriks CRUD-nya dengan tabel target bertipe `C` dan tabel sumber `SELECT` bertipe `R`.

**Reproduksi minimal.**

```sql
INSERT INTO arsip (id) SELECT id FROM pesanan;
```

**Akar masalah.** 
Menurut SPESIFIKASI.md bagian 3, aturan produksi statement `INSERT` memiliki dua cabang alternatif:
`insert_stmt = "INSERT" "INTO" table_name ... ( "VALUES" value_row ... | select_stmt )`.
Kode lama pada fungsi `_insert` di `crud/parser.py` hanya mengimplementasikan cabang `VALUES`. Ketika mendeteksi token `SELECT`, kode lama hanya berupa `TODO(T1)` yang langsung melempar `ParseError("INSERT ... SELECT belum didukung")`. Akibatnya, AST tidak pernah terbentuk dan pipeline berhenti sebelum tahap analisis CRUD.

**Perbaikan.** Pada file `crud/parser.py` di dalam method `_insert`, cabang `if self._check_kw("SELECT"):` diperbaiki dengan memanggil `query = self._select()` untuk mem-parse subquery tersebut, lalu mengembalikan objek `ast.Insert(table, columns, values=[], query=query, line=start.line)`.  


**Test regresi.**
- `test_regresi_crud_insert_into_select`
- `test_insert_select` (di `tests/test_parser.py`)

**Peran AI.** (Isikan peran AI di sini)
