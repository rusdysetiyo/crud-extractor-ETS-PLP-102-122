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

**Diperbaiki oleh:** Rusdya Setiyo Aji

**Gejala.** Input kueri SQL yang memuat komentar blok `/* ... */` menghasilkan error leksikal `LexError: Baris X, kolom Y: komentar blok belum didukung`. 
Output yang diharapkan menurut SPESIFIKASI.md bagian 2.3 adalah komentar blok diabaikan dan tidak menghasilkan token sama sekali, 
serta jika tidak ditutup hingga akhir berkas harus melempar `LexError`.

**Reproduksi minimal.**

```sql
/* komentar */ SELECT 1;
```

**Akar masalah.** Dalam buku Crafting Interpreters Bab 4 bagian 4.6 (Longer Lexemes) dan bagian 4.5.1 (*Lexical errors*), scanner bertugas mengonsumsi karakter kode dan mengelompokkannya menjadi token. 
Komentar apapun itu diklasifikasikan sebagai lexeme yang tidak memiliki nilai semantik bagi tahapan parser, sehingga pada kasus ini strategi pemindaiannya adalah mengonsumsi dan membuang seluruh karakter di antara delimiter pembuka (`/*`) dan penutup (`*/`) tanpa mengemisikan token ke parser, sambil tetap memelihara posisi baris/kolom. 
Selain itu, menurut bagian 4.5.1, jika pemindaian lexeme multi-karakter yang memiliki pembatas berpasangan mencapai akhir berkas (`EOF`) tanpa menemukan delimiter penutup, scanner wajib membangkitkan lexical error (*unterminated lexical structure*).
Pada kode lama di `crud/lexer.py`, saat karakter `/*` terdeteksi, program hanya berisi komentar `TODO(T3)` dan langsung melempar `LexError("komentar blok belum didukung", line, col)`. 
Kode tidak menjalankan loop *lookahead* untuk memindai karakter sampai token penutup `*/`. Hal ini melanggar konsep penanganan longer lexemes dan spesifikasi SQL pada SPESIFIKASI.md bagian 2.3.

**Perbaikan.** Pada file `crud/lexer.py`, di fungsi `_scan_token`, baris pelemparan error diganti dengan pemanggilan helper `self._block_comment(line, col)`. 
Fungsi ini memajukan pembacaan karakter menggunakan `_advance()`, mengabaikan karakter `*` biasa di dalam teks, melewati `*/` saat menemukannya dan berhenti, 
serta melempar `LexError("komentar blok tidak ditutup", line, col)` jika mencapai akhir input (`EOF`).  


**Test regresi.**
- `test_regresi_komentar_blok_tidak_ditutup_harus_error`
- `test_komentar_blok` (di `tests/test_lexer.py`)
- `test_kasus_tepi_komentar_blok_berisi_bintang`

**Peran AI.**  Membantu membuatkan test dengan skenario yang ditentukan

---

## Bug 4: Sintaks INSERT INTO ... SELECT Belum Didukung di Parser

**Diperbaiki oleh:** Rusdya Setiyo Aji

**Gejala.** Input kueri SQL berupa `INSERT INTO ... SELECT ...` menghasilkan error sintaks `ParseError: Baris X, kolom Y: INSERT ... SELECT belum didukung, ditemukan 'SELECT'`. Output yang diharapkan menurut SPESIFIKASI.md bagian 3 dan bagian 5 adalah kueri berhasil di-parse ke dalam node `ast.Insert` dengan subquery `query` yang valid, serta diekstrak matriks CRUD-nya dengan tabel target bertipe `C` dan tabel sumber `SELECT` bertipe `R`.

**Reproduksi minimal.**

```sql
INSERT INTO arsip (id) SELECT id FROM pesanan;
```

**Akar masalah.** 
Dalam buku Crafting Interpreters Bab 5 bagian 5.1 (*Context-Free Grammars*) dan Bab 6 bagian 6.2 (*Recursive Descent Parsing*), 
sebuah parser *recursive descent* mengimplementasikan aturan-aturan produksi grammar langsung ke dalam fungsi atau metode kode program. 
Ketika sebuah aturan produksi grammar memuat percabangan misalnya `( "VALUES" value_row ... | select_stmt )`), parser menggunakan token *lookahead* untuk melakukan *predictive parsing* dan memilih cabang fungsi parser yang sesuai.
Menurut SPESIFIKASI.md bagian 3, aturan produksi statement `INSERT` memiliki dua cabang alternatif:
`insert_stmt = "INSERT" "INTO" table_name ... ( "VALUES" value_row ... | select_stmt )`.
Kode lama pada fungsi `_insert` di `crud/parser.py` melanggar kelengkapan implementasi tata bahasa ini, parser hanya mengimplementasikan cabang `VALUES`. Ketika mendeteksi token `SELECT`, kode lama hanya berupa `TODO(T1)` yang langsung melempar `ParseError("INSERT ... SELECT belum didukung")` alih-alih mendelegasikan pemrosesan ke method `_select()`. Akibatnya, AST `ast.Insert` tidak pernah terbentuk dan pipeline terhenti sebelum tahap ekstraksi CRUD.

**Perbaikan.** Pada file `crud/parser.py` di dalam method `_insert`, cabang `if self._check_kw("SELECT"):` diperbaiki dengan memanggil `query = self._select()` untuk mem-parse subquery tersebut, lalu mengembalikan objek `ast.Insert(table, columns, values=[], query=query, line=start.line)`.  


**Test regresi.**
- `test_regresi_crud_insert_into_select`
- `test_insert_select` (di `tests/test_parser.py`)

**Peran AI.**  Membantu membuatkan test secara keseluruhan

---

## Bug 5: Operator Perbandingan <> Terpecah Menjadi Dua Token di Lexer

**Ditemukan oleh:** Rusdya Setiyo Aji · **Diperbaiki oleh:** Gharin Fawwaz

**Gejala.** Input query SQL yang menggunakan operator perbandingan tidak sama dengan `<>` menghasilkan error sintaks pada parser: `ParseError: Baris X, kolom Y: diharapkan ekspresi, ditemukan '>'`.
Output yang diharapkan menurut SPESIFIKASI.md bagian 2.5 adalah operator `<>` dikenali sebagai satu token utuh bertipe `OP` dengan nilai `"<>"`, bukan dua token terpisah (`<` lalu `>`)

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE x <> 1;
```

**Akar masalah.** 
Dalam buku Crafting Interpreters Bab 4 bagian 4.5.2 (*Operators*) dan bagian 4.7 (*Maximal Munch*), operator multi-karakter (seperti `!=`, `<=`, `>=`, atau `<>`) memerlukan teknik *lookahead* dua karakter menggunakan kondisional seperti `match()`.
Prinsip dasar *maximal munch* (aturan *longest match*) menyatakan bahwa ketika dua atau lebih aturan leksikal dapat mencocokkan deretan karakter input, pemindai wajib memilih aturan yang mengonsumsi karakter terbanyak. Pada SQL standar dan SPESIFIKASI.md bagian 2.5, deretan karakter `<>` adalah satu lexeme tunggal bernilai `"<>"`, bukan dua operator terpisah.
Pada fungsi `_scan_token` di `crud/lexer.py`, saat karakter `<` ditemukan, kode hanya mengecek apakah karakter berikutnya adalah `=` menggunakan `self._match("=")` untuk membentuk token `<=`. Kode belum memeriksa kemungkinan karakter `>`. Akibat melanggar prinsip *maximal munch* dan *lookahead* ini, lexer menganggap `<` telah selesai sebagai token `OP` tunggal, lalu di iterasi berikutnya membaca `>` sebagai token `OP` tersendiri. Akibatnya, parser menerima dua token operator perbandingan berturut-turut (`<` lalu `>`), yang tidak valid secara sintaksis dan memicu `ParseError`.

**Perbaikan.** Pada file crud/lexer.py di dalam fungsi _scan_token(), perbaikan dilakukan dengan menambahkan kondisi elif self._match(">"): di dalam blok percabangan untuk karakter <. Di dalam blok tersebut, variabel op diatur menjadi "<>". Perubahan ini membuat lexer mampu memeriksa dan menangkap karakter > tepat setelah <, menjadikannya satu token OP yang utuh sehingga tidak terpecah menjadi dua token terpisah.

**Test regresi.**
- `test_regresi_operator_tidak_sama_dengan` (di `tests/test_tambahan.py`)

**Peran AI.**  Membantu membuatkan test secara keseluruhhan dan membantu memperbaiki bug.

---

## Bug 6: Operasi Tabel Subquery pada Statement UPDATE Salah Ditandai sebagai 'U'

**Ditemukan oleh:** Rusdya Setiyo Aji · **Diperbaiki oleh:** Gharin Fawwaz

**Gejala.** Input statement `UPDATE` yang memuat subquery pada klausa `SET` maupun klausa `WHERE` menyebabkan tabel di dalam subquery salah dicatat sebagai operasi `U`.
Output yang diharapkan menurut SPESIFIKASI.md bagian 5 (Tabel aturan CRUD) adalah: tabel target `UPDATE` bertipe `U`, sedangkan membaca tabel lewat subquery **selalu R**, apa pun jenis statement luarnya.

**Reproduksi minimal.**

```sql
UPDATE pelanggan SET level = 'gold' WHERE id IN (SELECT pelanggan_id FROM pesanan);
```

**Akar masalah.**
Dalam buku Crafting Interpreters Bab 7 (*Evaluating Expressions*, bagian 7.2) dan Bab 8 (*Statements and State*, bagian 8.1), 
terdapat pemisahan antara statement dan expression. Statement berfungsi menghasilkan efek samping (perubahan state atau data), 
sedangkan expression untuk memproduksi nilai data tanpa mengubah state dari entitas luar. 
Saat melakukan penelusuran AST, nested expression seperti subquery pada predikat `WHERE` atau ekspresi nilai pada klausa `SET` hanya berperan mengevaluasi dan membaca data.
Pada fungsi `analyze_statement` di `crud/analyzer.py`, penanganan node `ast.Update` memanggil fungsi pembantu `_collect` untuk ekspresi nilai `SET` dan kondisi `WHERE` dengan meneruskan parameter operasi `"U"`:
`_collect(assignment.value, usage, "U")` dan `_collect(stmt.where, usage, "U")`.
Fungsi `_collect` bertugas mengumpulkan tabel di dalam subquery dan menandainya dengan operasi yang dioperkan. Karena dioperkan `"U"`, tabel-tabel di dalam subquery yang read-only keliru ditandai sebagai termodifikasi (`"U"`).

**Perbaikan.** Pada file crud/analyzer.py di dalam fungsi analyze_statement(), parameter operasi yang dilewatkan ke fungsi pembantu _collect diubah. Untuk penanganan percabangan ast.Update, pemanggilan fungsi untuk assignment.value maupun stmt.where yang semula dioper dengan "U" telah diganti menjadi "R". Perubahan ini memastikan bahwa semua tabel yang dibaca dari subquery pada statement UPDATE dianalisis dengan tepat sebagai operasi baca atau R.

**Test regresi.**
- `test_regresi_update_subquery_selalu_read` (di `tests/test_tambahan.py`)

**Peran AI.**  Membantu membuatkan test secara keseluruhhan dan membantu memperbaiki bug.

---

## Bug 7: Scope Statement DELETE Tidak Di-pop

**Ditemukan oleh:** Rusdya Setiyo Aji **Diperbaiki oleh:**  Gharin Fawwaz

**Gejala.** Ketika file SQL berisi statement `DELETE` dengan alias (misalnya `DELETE FROM pelanggan p`), lalu diikuti statement lain yang merujuk alias `p` padahal alias tersebut tidak dideklarasikan di statement kedua, resolver tidak melaporkan error dan malah berhasil meresolve alias tersebut ke tabel milik `DELETE`. Selain itu, setelah script selesai di-resolve, atribut `resolver.scope` masih menyisakan objek `Scope` (tidak kembali `None`).
Output yang diharapkan menurut SPESIFIKASI.md bagian 4.5 (*"Setiap statement berdiri sendiri. Setelah satu statement selesai di-resolve, tidak boleh ada scope tersisa. Alias dari statement sebelumnya tidak boleh terlihat oleh statement berikutnya."*) adalah: statement kedua wajib menghasilkan diagnostik error `alias 'p' tidak terdefinisi` dan `resolver.scope` harus bernilai `None`.

**Reproduksi minimal.**

```sql
DELETE FROM pelanggan p WHERE p.id = 1;
SELECT p.nama FROM pesanan o;
```

**Akar masalah.**
Dalam buku Crafting Interpreters Bab 8 bagian 8.5 serta Bab 11 bagian 11.3.1 (*Resolving blocks*), pengelolaan scope variabel diatur menggunakan scope stack. 
Ketika memasuki unit eksekusi/blok/statement baru, resolver harus membuat dan menaruh scope lokal baru di atas stack (`beginScope()` atau `_push()`). 
Selanjutnya, saat pemrosesan blok atau statement tersebut selesai dieksekusi, scope tersebut **wajib** dikeluarkan dari tumpukan (`endScope()` atau `_pop()`) untuk membatasi lifetime binding nama-nama lokal di dalamnya.
Pada file `crud/resolver.py`, fungsi `_delete` memanggil `self._push()` di awal untuk mendaftarkan tabel dan alias target `DELETE`, namun tidak memanggil `self._pop()` di akhir fungsi. 
Pelanggaran terhadap scope stack ini mengakibatkan kebocoran scope, scope lokal dari statement `DELETE` tetap tertinggal di `resolver.scope` dan memengaruhi statement-statement SQL berikutnya, sehingga alias dan tabel privat milik statement sebelumnya tidak terisolasi dan melanggar prinsip isolasi statement pada SPESIFIKASI.md bagian 4.5.


**Perbaikan.**Pada file crud/resolver.py, perbaikan dilakukan dengan menambahkan satu baris kode pemanggilan metode self._pop() di akhir fungsi _delete(). Perbaikan ini akan memastikan scope atau lingkungan yang dibuat pada saat pembacaan statement DELETE lewat self._push() dihapus saat statement tersebut selesai di-resolve, mencegah kebocoran scope ke statement SQL selanjutnya.

**Test regresi.**
- `test_regresi_scope_delete_tidak_bocor` (di `tests/test_tambahan.py`)

**Peran AI.**  Membantu membuatkan test secara keseluruhan dan membantu memperbaiki bug.

---

## Bug 8: Error Recovery (Panic Mode) di Parser Membuang Seluruh Kode sampai EOF

**Ditemukan oleh:** Rusdya Setiyo Aji · **Diperbaiki oleh:** Rusdya Setiyo Aji

**Gejala.** Ketika file SQL memuat statement yang gagal diparse, seluruh statement yang valid setelah statement gagal tersebut ikut terbuang dan tidak diekstrak ke dalam daftar statement.
Output yang diharapkan menurut SPESIFIKASI.md bagian 6 (*"Error recovery (panic mode): setelah error, buang token sampai dan termasuk ';' berikutnya, lalu lanjutkan dengan statement setelahnya. Setiap statement rusak menghasilkan tepat satu error, dan statement valid setelahnya tetap diproses."*) adalah statement rusak menghasilkan tepat satu `ParseError`, dan statement valid setelahnya tetap berhasil diproses dan disimpan ke `script.statements`.

**Reproduksi minimal.**

```sql
SELECT FROM;
SELECT id FROM pelanggan;
```

**Akar masalah.** Dalam buku Crafting Interpreters Bab 6 bagian 6.3 (*Syntax Errors*, khususnya 6.3.1 *Panic mode error recovery* dan 6.3.3 *Synchronizing a recursive descent parser*), 
teknik recovery error panic mode bekerja dengan membawa parser keluar dari tumpukan produksi aturan yang mengalami kegagalan, 
kemudian melakukan synchronization pada aliran token hingga menemukan batas pemisah statement (*synchronization boundary*). 
Dalam bahasa seperti SQL, titik koma (`;`) berperan sebagai pembatas akhir statement yang jelas. Dengan menyinkronkan pembacaan token hingga batas titik koma, parser dapat meredam kesalahan beruntun dan melanjutkan parsing pada statement berikutnya
Pada kode lama di `crud/parser.py`, fungsi `_synchronize()` hanya berupa loop `while not self._at_end(): self._advance()`. 
Loop ini membuang seluruh token tanpa henti hingga mencapai akhir berkas (`EOF`). 
Hal ini melanggar konsep synchronization pada *panic mode recovery*, alih-alih melompat ke pembatas statement berikutnya (`;`) agar parsing dapat dipulihkan, parser justru membuang semua statement valid yang berada di belakang statement yang rusak.

**Perbaikan.** Pada file `crud/parser.py`, method `_synchronize()` diperbaiki agar berhenti segera setelah menemukan dan mengonsumsi token titik koma (`T.SEMICOLON`):
```python
def _synchronize(self) -> None:
    # Panic mode (SPESIFIKASI.md bagian 6): buang token sampai
    # dan termasuk ';' berikutnya, lalu lanjutkan dengan statement setelahnya.
    while not self._at_end():
        if self._advance().type == T.SEMICOLON:
            return
```

**Test regresi.**
- `test_regresi_panic_mode_error_recovery` (di `tests/test_tambahan.py`)

**Peran AI.** Membantu membuatkan test dengan skenario yang ditentukan

---

## Bug 9: Presedensi Operator Logika AND dan OR Dianggap Setara di Parser

**Ditemukan oleh:** Rusdya Setiyo Aji · **Diperbaiki oleh:** Gharin Fawwaz

**Gejala.** Ekspresi logika campuran `AND` dan `OR` tanpa tanda kurung (seperti `a = 1 OR b = 2 AND c = 3`) dievaluasi secara dari kiri ke kanan, sehingga menghasilkan struktur `(a = 1 OR b = 2) AND c = 3`.
Output yang diharapkan menurut SPESIFIKASI.md bagian 3 dan 3.1 adalah operator `AND` memiliki tingkat presedensi lebih tinggi (tingkat 2) dibandingkan `OR` (tingkat 1), sehingga ekspresi harus dikelompokkan menjadi `a = 1 OR (b = 2 AND c = 3)`

**Reproduksi minimal.**

```sql
SELECT id FROM t WHERE a = 1 OR b = 2 AND c = 3;
```

**Akar masalah.**
Dalam buku Crafting Interpreters Bab 6 bagian 6.1 (subbab *Precedence and Associativity*) dan Bab 9 bagian 9.3 (*Logical Operators*), 
context-free grammar harus distratifikasi untuk menyelesaikan ambiguitas urutan evaluasi operator dan menegakkan presedensi operator secara hierarkis. 
Dalam teknik *stratified grammar*, setiap tingkatan presedensi diwakili oleh aturan produksi tata bahasa yang berbeda, 
aturan dengan presedensi lebih rendah (seperti `logic_or`) harus memanggil aturan dengan presedensi lebih tinggi (seperti `logic_and`), 
yang kemudian memanggil aturan di atasnya lagi (`equality` / perbandingan). Dengan struktur ini, operator dengan presedensi lebih tinggi akan mengikat lebih kuat dan menempati simpul yang lebih dalam pada ast.
Pada fungsi `_logical` di `crud/parser.py`, parser menggabungkan pengecekan `AND` dan `OR` ke dalam satu perulangan tunggal `while self._check_kw("AND", "OR"):`. Hal ini melanggar konsep *stratified grammar* dan memberlakukan presedensi datar (*flat precedence*) berasosiatif kiri pada kedua operator. Akibatnya, ekspresi seperti `a = 1 OR b = 2 AND c = 3` secara keliru dikelompokkan menjadi `(a = 1 OR b = 2) AND c = 3`, menyalahi aturan grammar berjenjang pada SPESIFIKASI.md bagian 3 (`or_expr = and_expr { "OR" and_expr }` dan `and_expr = not_expr { "AND" not_expr }`).

**Perbaikan.** Pada `crud/parser.py`, fungsi `_logical` dihapus dan diganti dua fungsi berjenjang, `_or_expr` dan `_and_expr`. `_expr` memanggil `_or_expr`; `_or_expr` memanggil `_and_expr` dan mengulang selama menemukan `OR`; `_and_expr` memanggil `_not` dan mengulang selama menemukan `AND`; `_not` kemudian memanggil `_comparison`. Dengan begitu `AND` diikat lebih dulu (lebih dalam di pohon) sebelum `OR` mengikat hasilnya di lapisan luar, dan keduanya tetap asosiatif kiri. Alternatif yang dipertimbangkan: (a) satu fungsi dengan tabel presedensi (*precedence climbing*), ditolak karena grammar spesifikasi sudah disusun per tingkat dan fungsi lain di file ini juga mengikuti pola satu fungsi per tingkat; (b) mempertahankan satu fungsi `_logical` lalu menyusun ulang pohon sesudahnya, ditolak karena rapuh dan tidak mengikuti grammar.

**Test regresi.**
- `test_regresi_presedensi_and_lebih_tinggi_dari_or` (di `tests/test_tambahan.py`)
- `test_kasus_tepi_presedensi_between_and_dengan_or` (di `tests/test_tambahan.py`)

**Peran AI.** Membantu membuatkan test dengan skenario yang ditentukan dan membantu memperbaiki bug.
