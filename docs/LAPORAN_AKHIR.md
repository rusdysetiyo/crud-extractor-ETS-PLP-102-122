# Laporan Akhir

## 1. Hasil evaluasi

Tempel keluaran `python evaluate.py` setelah `data/ground_truth.csv` dilengkapi.

```text

Dievaluasi: audit.sql, campuran_error.sql, laporan_penjualan.sql, pemeliharaan.sql (27 triple)

Metode   Precision  Recall     F1
parser        0.91    0.74   0.82
regex         0.65    0.81   0.72

[parser]
  salah ditemukan (FP): ('audit.sql', 20, 'pelanggan', 'U')
  salah ditemukan (FP): ('laporan_penjualan.sql', 12, 'pesanan', 'U')
  terlewat (FN):       ('audit.sql', 20, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pelanggan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 3, 'pesanan', 'R')
  terlewat (FN):       ('laporan_penjualan.sql', 12, 'pesanan', 'R')
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

1.
2.
3.

## 4. Pembagian kerja

Siapa mengerjakan apa, dan bagaimana kalian memastikan keduanya memahami seluruh kode.
