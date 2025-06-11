# Sistem Rekomendasi Buku

## 1. Project Overview

Membaca buku merupakan salah satu cara utama untuk memperoleh pengetahuan dan hiburan. Namun, dengan jumlah buku yang terus bertambah setiap tahunnya, pengguna sering kali mengalami kesulitan dalam menemukan buku yang relevan dan sesuai dengan minat mereka. Menurut laporan UNESCO, lebih dari 2,2 juta judul buku baru diterbitkan setiap tahun di seluruh dunia [^1]. Hal ini menyebabkan information overload, sehingga pengguna membutuhkan bantuan untuk menemukan buku yang tepat.

Sistem rekomendasi buku hadir sebagai solusi untuk membantu pengguna menemukan buku yang relevan secara personal. Berdasarkan riset oleh Ricci et al. (2015), sistem rekomendasi dapat meningkatkan kepuasan pengguna dan waktu yang dihabiskan pada platform digital. Goodreads, sebagai salah satu platform buku terbesar, juga mengandalkan sistem rekomendasi untuk meningkatkan engagement pengguna.

**Referensi:**

- [UNESCO Institute for Statistics, 2017](http://uis.unesco.org/en/topic/literacy)
- Ricci, F., Rokach, L., & Shapira, B. (2015). Recommender Systems Handbook. Springer.
- [Dataset: Goodreads Books 10k on Kaggle](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k)

---

## 2. Business Understanding

### Problem Statement

Pengguna sering mengalami kesulitan dalam menemukan buku yang relevan dan sesuai minat mereka di tengah banyaknya pilihan yang tersedia di platform digital seperti Goodreads. Tanpa sistem rekomendasi yang baik, pengguna harus mencari secara manual, yang memakan waktu dan seringkali tidak efektif.

### Goals

Membangun sistem rekomendasi buku yang dapat memberikan daftar top-N buku yang relevan dan personal untuk setiap pengguna, sehingga pengalaman mencari dan membaca buku menjadi lebih mudah, efisien, dan menyenangkan.

### Solution Approach

Untuk mencapai tujuan tersebut, digunakan dua pendekatan utama:

- **Content-based Filtering:** Sistem akan merekomendasikan buku berdasarkan kemiripan fitur seperti judul, penulis, dan tag. Jika pengguna menyukai satu buku, sistem akan mencari buku lain yang mirip dari sisi konten.
- **Collaborative Filtering:** Sistem akan merekomendasikan buku berdasarkan pola perilaku dan rating pengguna lain yang mirip. Dengan mempelajari kebiasaan banyak pengguna, sistem dapat memberikan rekomendasi yang lebih personal dan variatif.

Dengan kedua pendekatan ini, sistem rekomendasi dapat membantu pengguna menemukan buku yang sesuai dengan preferensi mereka, baik untuk pengguna baru (cold start) maupun pengguna lama yang sudah memiliki riwayat interaksi.

---

## 3. Data Understanding

Dataset yang digunakan berasal dari [Goodreads Books 10k](https://www.kaggle.com/datasets/zygmunt/goodbooks-10k) dan terdiri dari beberapa file utama:

- **books.csv**: Informasi detail tentang buku (10.000 baris)

  - `id`: ID internal dataset
  - `book_id`: ID unik untuk buku
  - `best_book_id`: ID buku versi terbaik
  - `work_id`: ID karya (work) di Goodreads
  - `books_count`: Jumlah edisi buku
  - `isbn`: ISBN 10 digit (700 missing values)
  - `isbn13`: ISBN 13 digit (700 missing values)
  - `authors`: Nama penulis
  - `original_publication_year`: Tahun terbit asli (1.000 missing values)
  - `original_title`: Judul asli (1.000 missing values)
  - `title`: Judul buku
  - `language_code`: Kode bahasa (1.000 missing values)
  - `average_rating`: Rata-rata rating
  - `ratings_count`: Jumlah rating
  - `work_ratings_count`: Jumlah rating pada karya
  - `work_text_reviews_count`: Jumlah review teks
  - `ratings_1` s/d `ratings_5`: Jumlah rating per skor
  - `image_url`, `small_image_url`: Link gambar sampul

- **ratings.csv**: Data rating user (981.756 baris)

  - `user_id`: ID user
  - `book_id`: ID buku
  - `rating`: Nilai rating (1-5)

- **book_tags.csv**: Relasi buku dan tag (999.912 baris)

  - `goodreads_book_id`: ID buku
  - `tag_id`: ID tag
  - `count`: Jumlah tag pada buku

- **tags.csv**: Daftar tag (34.252 baris)
  - `tag_id`: ID tag
  - `tag_name`: Nama tag

#### Kondisi Data

- Kolom `isbn`, `isbn13`, `original_publication_year`, `original_title`, dan `language_code` pada books.csv memiliki missing values.
- Data rating dan tag tidak memiliki missing values signifikan.

---

### Ringkasan Hasil EDA

#### 1. Struktur dan Kondisi Data `books.csv`

| Kolom                     | Non-Null Count | Missing Value | Tipe Data | Deskripsi                             |
| ------------------------- | -------------- | ------------- | --------- | ------------------------------------- |
| id                        | 10000          | 0             | int64     | ID internal dataset                   |
| book_id                   | 10000          | 0             | int64     | ID unik untuk buku                    |
| best_book_id              | 10000          | 0             | int64     | ID buku versi terbaik di Goodreads    |
| work_id                   | 10000          | 0             | int64     | ID karya (work) di Goodreads          |
| books_count               | 10000          | 0             | int64     | Jumlah edisi buku                     |
| isbn                      | 9300           | 700           | object    | ISBN 10 digit (700 missing values)    |
| isbn13                    | 9415           | 585           | float64   | ISBN 13 digit (585 missing values)    |
| authors                   | 10000          | 0             | object    | Nama penulis                          |
| original_publication_year | 9979           | 21            | float64   | Tahun terbit asli (21 missing values) |
| original_title            | 9415           | 585           | object    | Judul asli (585 missing values)       |
| title                     | 10000          | 0             | object    | Judul buku                            |
| language_code             | 8916           | 1084          | object    | Kode bahasa (1084 missing values)     |
| average_rating            | 10000          | 0             | float64   | Rata-rata rating                      |
| ratings_count             | 10000          | 0             | int64     | Jumlah rating                         |
| work_ratings_count        | 10000          | 0             | int64     | Jumlah rating pada karya              |
| work_text_reviews_count   | 10000          | 0             | int64     | Jumlah review teks                    |
| ratings_1                 | 10000          | 0             | int64     | Jumlah rating bintang 1               |
| ratings_2                 | 10000          | 0             | int64     | Jumlah rating bintang 2               |
| ratings_3                 | 10000          | 0             | int64     | Jumlah rating bintang 3               |
| ratings_4                 | 10000          | 0             | int64     | Jumlah rating bintang 4               |
| ratings_5                 | 10000          | 0             | int64     | Jumlah rating bintang 5               |
| image_url                 | 10000          | 0             | object    | Link gambar sampul                    |
| small_image_url           | 10000          | 0             | object    | Link gambar sampul kecil              |

**Insight:**  
Beberapa kolom pada books.csv memiliki missing value, terutama pada `isbn`, `isbn13`, `original_title`, dan `language_code`. Kolom rating dan review tidak memiliki missing value.

---

#### 2. Struktur dan Kondisi Data `ratings.csv`

| Kolom   | Non-Null Count | Missing Value | Tipe Data | Deskripsi          |
| ------- | -------------- | ------------- | --------- | ------------------ |
| book_id | 981756         | 0             | int64     | ID buku            |
| user_id | 981756         | 0             | int64     | ID user            |
| rating  | 981756         | 0             | int64     | Nilai rating (1-5) |

**Insight:**  
Tidak ada missing value pada ratings.csv. Sebagian besar user memberikan rating 4 atau 5 (berdasarkan visualisasi).

---

#### 3. Struktur dan Kondisi Data Tag

**book_tags.csv**

| Kolom             | Non-Null Count | Tipe Data | Deskripsi            |
| ----------------- | -------------- | --------- | -------------------- |
| goodreads_book_id | 999912         | int64     | ID buku di Goodreads |
| tag_id            | 999912         | int64     | ID tag               |
| count             | 999912         | int64     | Jumlah tag pada buku |

**tags.csv**

| Kolom    | Non-Null Count | Tipe Data | Deskripsi |
| -------- | -------------- | --------- | --------- |
| tag_id   | 34252          | int64     | ID tag    |
| tag_name | 34252          | object    | Nama tag  |

**Insight dari Visualisasi Tag:**

- **10 Tag Paling Sering Digunakan:**

| Tag               | Total Penggunaan |
| ----------------- | ---------------- |
| to-read           | 140,718,761      |
| currently-reading | 7,507,958        |
| favorites         | 4,503,173        |
| fiction           | 3,688,819        |
| fantasy           | 3,548,157        |
| young-adult       | 1,848,306        |
| classics          | 1,756,920        |
| books-i-own       | 1,317,235        |
| romance           | 1,231,926        |
| owned             | 1,224,279        |

Tag paling populer adalah 'to-read', 'currently-reading', dan 'favorites', yang menunjukkan aktivitas pembaca di Goodreads. Genre populer seperti 'fiction', 'fantasy', dan 'young-adult' juga sangat sering digunakan.

---

#### 4. Insight dari Visualisasi

- **Distribusi Average Rating Buku:**  
  Histogram menunjukkan mayoritas buku memiliki rating rata-rata di atas 3,5, menandakan buku-buku ini cukup disukai pembaca.

- **Distribusi Rating User:**  
  Countplot memperlihatkan sebagian besar user memberikan rating 4 atau 5, menunjukkan kecenderungan user untuk memberi rating tinggi.

- **Tag Terpopuler:**  
  Berdasarkan agregasi, tag paling sering digunakan adalah:

  1. to-read
  2. currently-reading
  3. favorites
  4. fiction
  5. fantasy
  6. young-adult
  7. classics
  8. books-i-own
  9. romance
  10. owned

  Ini menunjukkan genre dan aktivitas yang populer di Goodreads.

---

**Kesimpulan EDA:**

- Dataset relatif lengkap, namun ada beberapa kolom dengan missing value yang perlu diperhatikan pada tahap data preparation.
- Buku-buku di dataset cenderung memiliki rating tinggi.
- Genre populer diwakili oleh tag yang sering muncul, seperti fiction, fantasy, dan young-adult.

---

## 4. Data Preparation

Langkah data preparation yang dilakukan:

1. **Merge books dengan book_tags dan tags**  
   Untuk mendapatkan informasi tag pada setiap buku.

2. **Agregasi tag unik untuk setiap buku**  
   Menggabungkan semua tag yang dimiliki satu buku ke dalam satu kolom string.

3. **Penanganan missing value pada kolom 'tags'**  
   Mengisi nilai kosong dengan string kosong (`fillna('')`) agar tidak error saat rekayasa fitur.

4. **Filtering ratings**  
   Mengambil hanya rating untuk buku yang terdapat dalam `books_df`.

5. **Drop duplicates**  
   Menghapus duplikasi pada data rating (`ratings_filtered_df`) dan data buku (`books_content_df`) agar tidak terjadi bias.

6. **Rekayasa fitur konten**  
   Menggabungkan judul, penulis, dan tag menjadi satu fitur teks untuk content-based filtering.

7. **TF-IDF vectorization**  
   Mengubah fitur konten menjadi vektor numerik untuk menghitung kemiripan antar buku.

8. **Label encoding pada user_id dan book_id**  
   Mengubah ID menjadi angka agar dapat digunakan oleh algoritma collaborative filtering seperti LightFM.

---

**Alasan:**

- Penggabungan data membuat fitur konten lebih informatif.
- Penanganan missing value mencegah error saat proses rekayasa fitur.
- Filtering rating menjaga agar hanya data yang relevan yang digunakan.
- Menghapus duplikasi mencegah bias pada model.
- TF-IDF diperlukan untuk representasi teks dalam bentuk numerik.
- Label encoding dibutuhkan agar model bisa memproses data kategori dalam bentuk numerik.

---

## 5. Modeling

### Penjelasan Singkat: Content-based Filtering vs Collaborative Filtering

Pada sistem rekomendasi buku ini, digunakan dua pendekatan utama, yaitu **Content-based Filtering** dan **Collaborative Filtering**. Berikut penjelasan singkat mengenai kedua metode tersebut agar end user dapat memahami perbedaannya:

#### 1. Content-based Filtering

Content-based filtering adalah metode yang memberikan rekomendasi berdasarkan kemiripan fitur atau atribut dari item (dalam hal ini buku). Sistem akan menganalisis informasi seperti judul, penulis, dan tag pada setiap buku. Jika pengguna menyukai sebuah buku, maka sistem akan mencari buku lain yang memiliki kemiripan konten dengan buku tersebut.  
**Kelebihan:**

- Cocok untuk pengguna baru (cold start user).
- Tidak bergantung pada data interaksi pengguna lain.
- Mudah dijelaskan karena berbasis fitur yang jelas.

**Kekurangan:**

- Rekomendasi cenderung terbatas pada kemiripan konten saja.
- Sulit menangkap preferensi kompleks yang tidak tercermin dari fitur buku.

#### 2. Collaborative Filtering

Collaborative filtering adalah metode yang memberikan rekomendasi berdasarkan pola interaksi pengguna lain yang mirip. Sistem akan mempelajari kebiasaan rating dari banyak pengguna, sehingga dapat memberikan rekomendasi yang lebih personal. Jika ada dua pengguna yang memiliki selera mirip, maka buku yang disukai oleh satu pengguna bisa direkomendasikan ke pengguna lain.  
**Kelebihan:**

- Dapat menangkap pola preferensi yang kompleks dan tersembunyi.
- Rekomendasi lebih variatif dan personal.

**Kekurangan:**

- Membutuhkan data interaksi yang cukup banyak.
- Mengalami masalah cold start untuk pengguna atau item baru.

---

### a. Content-based Filtering

Pada pendekatan ini, sistem mencari buku yang mirip berdasarkan isi (judul, penulis, tag).  
Misal, jika Anda suka buku "Harry Potter", maka sistem akan mencari buku lain yang mirip dari sisi konten.

Berikut contoh output Top-10 rekomendasi buku berdasarkan kemiripan konten:
| Title | Authors | Similarity Score |
| ---------------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------- |
| _What to Expect When You're Expecting_ | Heidi Murkoff, Arlene Eisenberg, Sandee Hathaway | **0.809673** |
| _The Happiest Baby on the Block: The New Way to Calm Crying and Help Your Newborn Baby Sleep Longer_ | Harvey Karp | **0.792327** |
| _Healthy Sleep Habits, Happy Child_ | Marc Weissbluth | **0.752592** |
| _On Becoming Baby Wise: Giving Your Infant the Gift of Nighttime Sleep_ | Gary Ezzo | **0.711568** |
| _NurtureShock: New Thinking About Children_ | Po Bronson, Ashley Merryman | **0.625052** |
| _Belly Laughs: The Naked Truth About Pregnancy and Childbirth_ | Jenny McCarthy | **0.603049** |
| _Bringing Up Bébé: One American Mother Discovers the Wisdom of French Parenting_ | Pamela Druckerman, Abby Craden | **0.590687** |
| _How to Talk So Kids Will Listen & Listen So Kids Will Talk_ | Adele Faber, Elaine Mazlish, Kimberly Ann Coe | **0.590128** |
| _Ina May's Guide to Childbirth_ | Ina May Gaskin | **0.499076** |
| _The Five Love Languages of Children_ | Gary Chapman, D. Ross Campbell | **0.395620** |

---

### b. Collaborative Filtering (LightFM)

Pada pendekatan ini, sistem akan merekomendasikan buku berdasarkan pola interaksi pengguna lain yang mirip.  
Model akan mempelajari kebiasaan rating dari banyak pengguna, sehingga bisa memberikan rekomendasi yang lebih personal, bahkan untuk buku yang belum pernah dibaca user.

Berikut contoh output Top-10 rekomendasi buku untuk user berdasarkan collaborative filtering (LightFM):

| Title                                                                           | Authors                                       |
| ------------------------------------------------------------------------------- | --------------------------------------------- |
| _Harry Potter and the Order of the Phoenix (Harry Potter, #5)_                  | J.K. Rowling, Mary GrandPré                   |
| _Harry Potter and the Half-Blood Prince (Harry Potter, #6)_                     | J.K. Rowling, Mary GrandPré                   |
| _The Ultimate Hitchhiker's Guide to the Galaxy_                                 | Douglas Adams                                 |
| _A Short History of Nearly Everything_                                          | Bill Bryson                                   |
| _Heidi_                                                                         | Johanna Spyri, Angelo Rinaldi, Beverly Cleary |
| _Notes from a Small Island_                                                     | Bill Bryson                                   |
| _I'm a Stranger Here Myself: Notes on Returning to America After 20 Years Away_ | Bill Bryson                                   |
| _Heretics of Dune (Dune Chronicles #5)_                                         | Frank Herbert                                 |
| _The Lord of the Rings: The Art of The Fellowship of the Ring_                  | Gary Russell                                  |
| _The Mother Tongue: English and How It Got That Way_                            | Bill Bryson                                   |

---

## 6. Evaluation

### Evaluasi Content-Based Filtering

Model content-based filtering dievaluasi menggunakan metrik **Precision@10** pada data test.  
Precision@10 mengukur seberapa banyak rekomendasi yang benar-benar relevan dari 10 rekomendasi teratas yang diberikan model.

**Hasil: Precision@10 (Content-Based Filtering): 0.0019**

Nilai precision@10 sebesar **0.0019** berarti, dari seluruh user yang dievaluasi, rata-rata hanya sekitar 0.19% dari 10 rekomendasi teratas yang benar-benar relevan (pernah diberi rating tinggi oleh user tersebut). Nilai ini cukup kecil, yang umum terjadi pada content-based filtering di dataset besar, terutama jika user hanya memiliki sedikit buku relevan di data test.

---

### Evaluasi Collaborative Filtering (LightFM)

Model collaborative filtering dievaluasi menggunakan metrik **Precision@10** dan **Recall@10** pada data training.

- **Precision@10**: Proporsi buku relevan di antara 10 rekomendasi teratas.
- **Recall@10**: Proporsi buku relevan yang berhasil ditemukan dari seluruh buku relevan untuk user.

- **Precision@10 (train): 0.1946**
- **Recall@10 (train): 0.8737**

Penjelasan:

- **Precision@10 sebesar 0.1946** artinya, dari 10 rekomendasi teratas yang diberikan model collaborative filtering (LightFM) kepada setiap user, rata-rata sekitar 19,46% di antaranya benar-benar relevan (pernah diberi rating tinggi oleh user tersebut).
- **Recall@10 sebesar 0.8737** berarti, dari seluruh item relevan yang dimiliki user, sekitar 87,37% berhasil ditemukan dalam 10 rekomendasi teratas yang diberikan model.

Nilai precision dan recall yang cukup tinggi ini menunjukkan bahwa model collaborative filtering mampu memberikan rekomendasi yang relevan dan mencakup sebagian besar item yang memang disukai oleh user.

---

## 7. Kesimpulan

Pada proyek ini, telah dikembangkan sistem rekomendasi buku menggunakan dua pendekatan utama: **content-based filtering** dan **collaborative filtering (LightFM)**. Evaluasi dilakukan dengan metrik **Precision@10** dan **Recall@10** untuk menilai relevansi rekomendasi.

### Hasil Evaluasi

- **Content-Based Filtering**  
  Precision@10: **0.0019**. Artinya, dari 10 rekomendasi teratas, rata-rata hanya 0,19% yang benar-benar relevan. Nilai rendah ini umum terjadi pada dataset besar dan user dengan riwayat interaksi terbatas.
- **Collaborative Filtering (LightFM)**  
  Precision@10: **0.1946**, Recall@10: **0.8737**. Model ini mampu menemukan sekitar 19,46% rekomendasi relevan di 10 teratas, dan mencakup 87,37% dari seluruh item relevan milik user—jauh lebih baik dibanding content-based.

### Insight Utama

- Mayoritas buku memiliki rating di atas 3,5; sebagian besar user memberi rating 4 atau 5 (bias positif).
- Genre populer: _fiction_, _fantasy_, dan _young-adult_.
- **Content-based filtering** cocok untuk cold start (user baru), tapi kurang efektif jika data terbatas.
- **Collaborative filtering** unggul untuk user dengan riwayat interaksi, karena dapat mengenali pola preferensi yang kompleks.

### Kelebihan & Kekurangan

| Pendekatan              | Kelebihan                                        | Kekurangan                                          |
| ----------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Content-Based Filtering | Mudah dijelaskan, tidak butuh banyak interaksi   | Kurang efektif jika data user/item terbatas         |
| Collaborative Filtering | Menangkap pola preferensi kompleks, akurasi baik | Membutuhkan banyak data interaksi, cold start issue |

### Saran Pengembangan

- Tambahkan **side information** (genre, tahun terbit, sinopsis) untuk memperkaya fitur.
- Evaluasi pada **test set** untuk mengukur generalisasi model.
- Implementasi **hybrid recommender system** untuk menggabungkan keunggulan kedua pendekatan.
- Sediakan **visualisasi tambahan** (distribusi rating/interaksi) untuk analisis lebih lanjut.
- Uji sistem pada **data nyata** atau lakukan **A/B testing** di aplikasi.

### Penutup

Sistem rekomendasi ini diharapkan membantu pengguna menemukan buku yang relevan dengan minat mereka, sehingga meningkatkan pengalaman membaca, keterlibatan, dan retensi pengguna pada platform buku digital.

---

[^1]: UNESCO Institute for Statistics, 2017. [Link](http://uis.unesco.org/en/topic/literacy)
