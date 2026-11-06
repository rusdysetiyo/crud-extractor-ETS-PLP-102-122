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

**Akar masalah.** Kode lama membandingkan teks apa adanya (`text in KEYWORDS`), padahal `KEYWORDS` hanya berisi huruf besar. Python membedakan `"where"` dan `"WHERE"`, sehingga pencocokan gagal. Lexer tidak melaporkan error karena bagi lexer `where` sah sebagai nama (`IDENT`).

Error baru muncul di parser, bukan di lexer. Parser membaca `FROM t`, lalu menganggap `where` sebagai alias tabel `t`, karena grammar mengizinkan alias berupa `IDENT` setelah nama tabel. Setelah alias, parser mengharapkan `;` atau keyword lanjutan, tetapi menemukan `x`, sehingga error dilaporkan di sana.

Konsep ini ada di *Crafting Interpreters* Bab 4 bagian 4.7: scanner membaca satu kata utuh terlebih dahulu, baru kemudian memeriksa apakah kata itu reserved word. Alur di kode sudah mengikuti urutan itu dengan benar. yang salah adalah langkah pengecekannya, yang peka huruf besar/kecil dan tidak menormalisasi nilai. Hal ini melanggar SPESIFIKASI 2.2, yaitu keyword tidak peka huruf besar/kecil dan nilai token keyword selalu dinormalisasi ke huruf besar.

**Perbaikan.** Pada `crud/lexer.py`, fungsi `_word`, ada dua perubahan: pengecekan ke `KEYWORDS` memakai `text.upper()`, dan nilai token keyword disimpan dalam huruf besar. Alternatif yang dipertimbangkan: (a) mengubah isi `KEYWORDS` menjadi huruf kecil, ditolak karena melanggar spesifikasi nilai huruf besar dan merusak parser, sedangkan alternatif (b) mengubah seluruh teks SQL menjadi huruf besar sebelum di-lexing, ditolak karena merusak data dan posisi kolom.

**Test regresi.** 
test_regresi_keyword_campuran_huruf: gagal sebelum perbaikan (token IDENT), lulus sesudahnya.
test_kata_berawalan_keyword_tetap_ident: lulus sebelum dan sesudah. berfungsinya sebagai penjaga supaya perbaikan tidak berlebihan.

**Peran AI.** ya AI sangat membantuku menemukan bug ini, AI menujukan lokasi peyebab dan kode perbaikan, selain itu saya juga meminta AI untuk menjelaskan code dan juga akar masalah yang dasar teorinya kurang saya pahami, saya memverifikasinya hasilnya menggunakan pytest, pengecekan manual dengan python -c, dan membandingkan dengan spesifikasi 2.2.

### Bug 2: Resolusi Kolom Tanpa Qualifier Belum Diimplementasikan (TODO 2)

**Ditemukan oleh:** Gharin Fawwaz  **Diperbaiki oleh:** Gharin Fawwaz

**Gejala:** Ketika terdapat kolom tanpa qualifier pada scope yang memiliki lebih dari satu tabel, sistem gagal mendeteksi keambiguan tersebut. Output yang didapat: atribut resolved dibiarkan kosong dan tidak ada peringatan apa pun. Output yang diharapkan menurut SPESIFIKASI.md 4.3: sistem harus mengeluarkan warning

**Reproduksi minimal:**
SELECT nama FROM pelanggan p, pesanan o

**Akar masalah.**Dalam buku Crafting Interpreters Bab 11: Resolving and Binding, sebuah resolver bertanggung jawab untuk mengikat  setiap variabel ke deklarasinya secara leksikal. Kode lama hanya menggunakan blok pass dan gagal menelusuri environment (scope) untuk melakukan binding statis pada kolom tersebut, sehingga interpreter kehilangan jejak asal usul kolom.

**Perbaikan.**File yang diubah adalah crud/resolver.py pada fungsi _column. Perbaikan dilakukan dengan mengekstrak nilai dari self.scope.entries dan mengecek jumlah tabelnya. Jika tepat 1, resolve ke tabel tersebut; jika > 1, keluarkan warning ambigu; jika 0, keluarkan warning tidak ada tabel. Alternatif yang dipertimbangkan adalah membiarkan program menebak salah satu tabel secara acak saat ambigu, namun ditolak karena dapat menyebabkan silent error yang berbahaya pada matriks tabel.

**Test regresi.** test_kolom_tanpa_qualifier_dua_tabel_ambigu

**Peran AI.**ya, AI membantu merumuskan logika percabangan untuk pengecekan entri pada scope serta menyusun fungsi pengujian.