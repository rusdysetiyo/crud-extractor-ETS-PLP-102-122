# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        1.00    0.89   0.94
regex         0.65    0.81   0.72

[parser]
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 8, 'crm.pelanggan', 'U')

[regex]
  salah ditemukan (FP): ('audit.sql', 16, 'sesi', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 4, 'pesanan', 'R')
  salah ditemukan (FP): ('campuran_error.sql', 8, 'keranjang', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'D')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pelanggan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'pesanan', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 2, 'rahasia', 'R')
  salah ditemukan (FP): ('laporan_penjualan.sql', 15, 'pesanan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.alamat', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'crm.pelanggan', 'R')
  salah ditemukan (FP): ('pemeliharaan.sql', 2, 'pelanggan_lama', 'U')
  salah ditemukan (FP): ('pemeliharaan.sql', 15, 'crm.alamat', 'R')
  terlewat (FN):       ('audit.sql', 2, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.alamat', 'R')
  terlewat (FN):       ('pemeliharaan.sql', 3, 'crm.pelanggan', 'R')
```

## 2. Tiga kasus di mana regex salah

Untuk tiap kasus: SQL-nya, kesalahan regex, dan mengapa parser benar (kaitkan dengan konsep
lexing, parsing, atau resolusi).

1. **Keyword dan Tabel di dalam Komentar (Komentar Baris dan Komentar Blok)**
   - **Contoh SQL:**
     ```sql
     -- Pada data/sample/laporan_penjualan.sql baris 2:
     -- DELETE FROM pelanggan   (baris ini komentar, bukan perintah)

     -- Pada data/sample/pemeliharaan.sql baris 1-2:
     /* Skrip pemeliharaan data pelanggan.
        Catatan lama: UPDATE pelanggan_lama sudah tidak dipakai. */
     ```
   - **Kesalahan regex:** Regex tidak mengenal komentar. Akibatnya, regex mendeteksi operasi palsu berupa operasi `DELETE` pada tabel `pelanggan` dan operasi `UPDATE` pada tabel fiktif `pelanggan_lama` padahal teks tersebut berada di dalam komentar.
   - **Mengapa parser benar (Konsep Lexing):** Pada tahap analisis leksikal, lexer menyaring karakter yang tidak bermakna bagi program. Komentar baris (`--`) dan komentar blok (`/* ... */`) dilewati tanpa menghasilkan token apa pun ke parser. Karena tidak ada token `DELETE`, `UPDATE`, atau identifier tabel yang dihasilkan, parser tidak pernah melihat teks tersebut sebagai statement SQL.

2. **Literal String yang Memuat Kata Kunci SQL (`'FROM ...'` di dalam Nilai Teks)**
   - **Contoh SQL:**
     ```sql
     -- Pada data/sample/laporan_penjualan.sql baris 6:
     WHERE o.status = 'LUNAS' AND o.catatan <> 'FROM rahasia'
     ```
   - **Kesalahan regex:** Regex mencocokkan kata `FROM rahasia` di dalam tanda kutip dengan pola `\bUPDATE\s+ + _NAME, re.I`. Akibatnya, regex salah mendeteksi adanya masalah, padahal sebenarnya aman dengan mencatat adanya operasi `R` (*Read*) pada tabel palsu bernama `rahasia`.
   - **Mengapa parser benar (Konsep Lexing dan Parsing):** 
     - Pada tahap **lexing**, teks yang diawali tanda kutip tunggal `'` dikelompokkan sebagai satu token bernilai literal (`TokenType.STRING`), bukan sebagai keyword `FROM` dan identifier `rahasia`.
     - Pada tahap **parsing**, token string ini berada di sisi kanan operator perbandingan pada pohon ekspresi klausa `WHERE`. Parser membedakan antara ekspresi nilai data dengan sumber data tabel pada klausa `FROM`, sehingga tidak ada tabel palsu yang diekstrak.

3. **Daftar Tabel Dipisahkan Koma pada Klausa FROM (*Multiple Tables / Comma Join*)**
   - **Contoh SQL:**
     ```sql
     -- Pada data/sample/audit.sql baris 2-3:
     SELECT p.id, p.nama
     FROM pelanggan p, pesanan o
     ```
   - **Kesalahan regex:** Pola regex `\bUPDATE\s+ + _NAME, re.I` hanya dirancang untuk mengambil tepat satu kata setelah keyword `FROM`. Akibatnya, regex hanya menangkap tabel pertama (`pelanggan`), sementara tabel kedua (`pesanan`) yang dipisahkan oleh tanda koma dilewatkan begitu saja
   - **Mengapa parser benar (Konsep Parsing / Grammar Rekursif):** Parser recursive descent bekerja berdasarkan grammar di spesifikasi
     `select_stmt = "SELECT" ... "FROM" table_ref { "," table_ref }`
     Parser memeriksa keberadaan token koma secara berulang dalam loop `while self._match(T.COMMA): sources.append(self._table_ref())`. Dengan demikian, berapa pun jumlah tabel yang digabungkan menggunakan tanda koma, seluruh tabel bisa ditampung ke dalam list `sources` pada node AST `Select`, dan kemudian analyzer menandai seluruh tabel tersebut dengan operasi `R`.


## 3. Batas pendekatan kami

Minimal tiga hal yang **tidak bisa** ditangani dengan benar oleh tool ini meskipun semua bug
sudah diperbaiki. Untuk tiap batas: contoh SQL atau situasinya, akibatnya pada CRUD matrix,
dan informasi apa yang dibutuhkan untuk mengatasinya.

1. **Ketiadaan Skema Database untuk Resolusi Kolom Ambigu (*No Schema Catalog*)**
   - **Contoh SQL / Situasi:**
     ```sql
     SELECT nama, total
     FROM pelanggan, pesanan
     WHERE pelanggan.id = pesanan.pelanggan_id;
     ```
   - **Akibat pada CRUD matrix:**
     Sesuai batasan arsitektur (SPESIFIKASI.md bagian 7 poin 4), tool ini bekerja murni dari teks query tanpa koneksi ke database maupun definisi skema tabel. Akibatnya, ketika ada kolom tanpa qualifier (`nama`, `total`) pada kueri yang melibatkan lebih dari satu tabel, resolver tidak dapat mengetahui kolom mana yang menjadi milik tabel mana. Atribut `resolved` pada kolom tersebut tetap `None` (hanya menghasilkan warning). Pada analisis penggunaan kolom (`--kolom`), relasi tabel-ke-kolom menjadi hilang atau tidak tercatat.
   - **Informasi yang dibutuhkan untuk mengatasinya:**
     Dibutuhkan **katalog skema database** yang memetakan setiap tabel fisik ke daftar kolom yang dimilikinya misalnya `pelanggan` memiliki kolom `[id, nama]` dan `pesanan` memiliki `[id, pelanggan_id, total]`, sehingga resolver dapat mencocokkan kolom tanpa qualifier ke tabel pemiliknya secara pasti.

2. **Abstraksi View Database, Stored Procedure, dan Trigger**
   - **Contoh SQL / Situasi:**
     ```sql
     SELECT * FROM v_laporan_keuangan;
     ```
     Di mana `v_laporan_keuangan` di database adalah sebuah *View* yang dibentuk dari:
     ```sql
     CREATE VIEW v_laporan_keuangan AS
     SELECT p.nama, t.nominal FROM pelanggan p JOIN transaksi t ON p.id = t.pelanggan_id;
     ```
   - **Akibat pada CRUD matrix:**
     Tool hanya mencatat operasi `R` pada nama objek `v_laporan_keuangan`. Tool sama sekali tidak mendeteksi bahwa tabel yang sesungguhnya diakses adalah tabel `pelanggan` dan `transaksi`. Akibatnya, matriks CRUD kehilangan operasi baca pada tabel-tabel fisik tersebut. Hal serupa terjadi pada `INSERT` atau `UPDATE` yang memicu *Trigger* atau prosedur tersimpan di database.
   - **Informasi yang dibutuhkan untuk mengatasinya:**
     Dibutuhkan definisi DDL dari seluruh view (*view definition*) dan trigger di database agar analyzer dapat melakukan ekspansi view (*view inlining/expansion*) ke dalam AST sebelum tahap analisis CRUD dilakukan.

3. **Konstruksi SQL Lanjutan di Luar Lingkup Grammar**
   - **Contoh SQL / Situasi:**
     ```sql
     WITH ringkasan AS (
         SELECT pelanggan_id, SUM(total) AS omzet FROM pesanan GROUP BY pelanggan_id
     )
     UPDATE pelanggan SET level = 'VIP'
     WHERE id IN (SELECT pelanggan_id FROM ringkasan WHERE omzet > 1000000);
     ```
   - **Akibat pada CRUD matrix:**
     Sintaks CTE (`WITH ... AS (...)`), `UNION`, dan `MERGE` berada di luar lingkup grammar parser yang didukung (SPESIFIKASI.md bagian 9). Saat kueri semacam ini dimasukkan, parser akan melempar `ParseError` karena tidak mengenali keyword pembuka `WITH`. Karena aturan spesifikasi menyatakan statement yang gagal di-parse tidak dihitung, seluruh operasi penting pada kueri tersebut (operasi `U` pada `pelanggan` dan `R` pada `pesanan`) diabaikan
   - **Informasi yang dibutuhkan untuk mengatasinya:**
     Dibutuhkan perluasan grammar pada parser recursive descent agar mampu mem-parse klausa `WITH`, serta penyesuaian pada resolver untuk menangani scope tabel semu sebelum tabel target dianalisis oleh analyzer.


## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.

### Rincian Pembagian Kerja:

* **Gharin Fawwaz**:
  - **Bug 1 (Lexer):** Menemukan dan memperbaiki masalah normalisasi keyword case-insensitive di `crud/lexer.py`
  - **Bug 2 / TODO 2 (Resolver):** Menemukan dan mengimplementasikan resolusi kolom tanpa qualifier untuk scope tunggal serta deteksi warning ambiguitas untuk scope jamak di `crud/resolver.py`.
  - **Bug 5 (Lexer):** Memperbaiki operator perbandingan `<>` di `crud/lexer.py` agar diproses sebagai satu kesatuan token `OP`
  - **Bug 6 (Analyzer):** Memperbaiki penandaan operasi tabel pada subquery di klausa `SET` dan `WHERE` statement `UPDATE` di `crud/analyzer.py` agar bertipe `'R'`.
  - **Bug 7 (Resolver):** Memperbaiki siklus hidup scope statement `DELETE` di `crud/resolver.py` dengan menambahkan `self._pop()` agar tidak bocor ke statement berikutnya.

* **Rusdya Setiyo Aji**:
  - **Bug 3 / TODO 3 (Lexer):** Mengimplementasikan dukungan komentar blok `/* ... */` (lintas baris, memuat karakter `*`, dan penanganan `LexError` jika tidak ditutup) di `crud/lexer.py`.
  - **Bug 4 / TODO 1 (Parser):** Mengimplementasikan dukungan parsing sintaks `INSERT INTO ... SELECT` di `crud/parser.py`.
  - **Bug 8 (Parser):** Menemukan dan memperbaiki mekanisme error recovery (*panic mode*) pada `_synchronize()` di `crud/parser.py` agar berhenti di batasan statement (`;`) dan tidak membuang statement valid berikutnya.
  - **Pengujian & Ground Truth:** Menemukan akar masalah serta menyusun unit test regresi dan kasus tepi di `tests/test_tambahan.py` (untuk Bug 3, 4, 5, 6, 7, dan 8), serta melengkapi data evaluasi manual di `data/ground_truth.csv` untuk berkas `audit.sql` dan `pemeliharaan.sql`.

---

### Cara Memastikan Keduanya Memahami Seluruh Kode:

Kami menerapkan pembagian peran berbasis TDD dan peer code reviw: salah satu anggota bertugas menganalisis spesifikasi, mereproduksi bug, dan menulis test regresi yang awalnya berstatus gagal (*Red*), sementara anggota lainnya membedah kode sumber, 
menerapkan logika perbaikan hingga test lulus (*Green*), lalu keduanya memverifikasi bersama dengan `pytest`.
Yang menemukan bug dan menambahkan unit test menjelaskan gejala dan akar masalahnya dan spesifikasi mana yang dilanggar,
Yang memperbaiki menjelaskan cara dan alur perbaikannya
Walau mungkin ada beberapa yang melakukan keduanya sekaligus.


