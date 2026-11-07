# Log Penggunaan AI

Catat setiap penggunaan AI atau coding agent yang memengaruhi kode atau laporan.

| No | Siapa              | Prompt / tugas (ringkas)                                                                      | Hasil: diterima, diubah, atau ditolak | Alasan                                                            | Cara verifikasi |
|----|--------------------|-----------------------------------------------------------------------------------------------| --- |-------------------------------------------------------------------| --- |
| 1  | Gharin Fawwaz      | Minta penjelasan langkah memperbaiki bug keyword huruf kecil                                  | Diterima, test saya tulis ulang| karena sesuai spesifikasi 2.2                                     |menggunakan pytest |
| 2  | Rusdya Setiyo Aji  | Memberikan ide penyelesaian todo 3 untuk direview, kalau tidak ada salah logika tulis kodenya | Diterima | Kode yang ditulis sesuai dengan ide                               | Dari kesesuaian kode dengan ide|
| 3  | Gharin Fawwaz      | Minta langkah mengerjakan Todo 2 dan jelaskan logikanya                                       | diterima | karena sesuai dengan spesifikasi                                  | pytest dan membandingkan dengan spesifikasi |
| 4  | Gharin Fawwaz      | Minta penjelasan langkah memperbaiki bug 5                                                    | diterima | karena membantu pengerjaan                                        | dibaca apakah sesuai dengan yang diminta dan membandingkan dengan SFESIFIKASI |
| 5  | Gharin Fawwaz      | Minta penjelasan langkah memperbaiki bug 6                                                    | diterima | karena membantu pengerjaan                                        | dibaca apakah sesuai dengan yang diminta dan membandingkan dengan SFESIFIKASI |
| 6  | Gharin Fawwaz      | Minta penjelasan langkah memperbaiki bug 7                                                    | diterima | karena membantu pengerjaan                                        | dibaca apakah sesuai dengan yang diminta dan membandingkan dengan SFESIFIKASI |
| 7  | Gharin Fawwaz      | Contoh dan Penjelasan Laporan_bug                                                             | Diterima tapi untuk laporannya di buat versi sendiri |                                                                   | --- |
| 8  | Rusdya Setiyo Aji  | Meminta untuk membuatkan unit test berdasarkan skenario yang saya berikan                     | Diterima | Alasan diterima karena sesuai dengan seknario                     | Membandingkannya dengan skenario test saya |
| 9  | Rusdya Setiyo Aji  | Meminta untuk membuatkan unit test secara keseluruhan                                         | Diterima | Alasan diterima, test yang dibuat benar menguji bug yang diminta  | Dengan menelaah alur skenario unit test yang dibuat, apakah ia benar menguji bug yang ditemukan|
| 10 | Rusdya Setiyo Aji  | Menanyakan tujuan baris kode spesifik di unit test tertentu                                   | Diterima | Penjelasan tidak terlihat melenceng dari baris yang dimaksud | Menelaah penjelasannya apakah tampak melenceng atau tidak|
| 11 | Rusdya Setiyo Aji | Meminta untuk mencarikan bug tersisa dan spesifikasi yang dilanggarnya                        | Diterima | Alasan diterima karena justifikasi atas spesifikasi yang dilanggar valid | Dengan melihat langsung bagian kode yang dianggap melanggar spesifikasi, apakah benar atau tidak|

**Refleksi (3-5 kalimat).** Di bagian mana AI paling membantu? Di mana AI keliru atau
menyesatkan, dan bagaimana kalian mengetahuinya?
Selama pengerjaan tidak ada jawaba sesat dari AI. AI paling membantu untuk menjelaskan langkah/cara dan baris kode, karena tentu saja percuma meminta AI membuatkan kode tanpa memahaminya, 
Meski begitu penjelasan AI tidak ditelah mentah begitu saja, ada langkah verifikasi dengan menelusuri langsung kode dan membandingkannya dengan penjelasannya.
