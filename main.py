import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, recall_at_k
from scipy import sparse
import os

DATA_PATH = './data/'

def load_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: Folder '{DATA_PATH}' not found. Please ensure the dataset is uploaded.")
        return None
    books_df = pd.read_csv(os.path.join(DATA_PATH, 'books.csv'))
    ratings_df = pd.read_csv(os.path.join(DATA_PATH, 'ratings.csv'))
    book_tags_df = pd.read_csv(os.path.join(DATA_PATH, 'book_tags.csv'))
    tags_df = pd.read_csv(os.path.join(DATA_PATH, 'tags.csv'))
    print("CSV files loaded:")
    print(f"book_tags.csv: {len(book_tags_df)} rows")
    print(f"tags.csv: {len(tags_df)} rows")
    print(f"ratings.csv: {len(ratings_df)} rows")
    print(f"books.csv: {len(books_df)} rows")
    return books_df, ratings_df, book_tags_df, tags_df

def eda(books_df, ratings_df, book_tags_df, tags_df):
    print("\n--- EDA ---")
    print(books_df.info())
    print(books_df.head())
    plt.figure(figsize=(10, 5))
    sns.histplot(books_df['average_rating'], bins=20, kde=True)
    plt.title('Distribution of Average Book Ratings')
    plt.savefig('images/distribution_average_book_ratings.png')
    plt.show()

    print(ratings_df.info())
    print(ratings_df.head())
    plt.figure(figsize=(8, 5))
    sns.countplot(x='rating', data=ratings_df, palette='viridis')
    plt.title('Distribution of User Ratings')
    plt.savefig('images/distribution_user_ratings.png')
    plt.show()

    book_tags_merged_df = pd.merge(book_tags_df, tags_df, on='tag_id', how='left')
    print(book_tags_merged_df.head())
    print("Top 10 Most Used Tags:")
    print(book_tags_merged_df.groupby('tag_name')['count'].sum().sort_values(ascending=False).head(10))

def data_preparation(books_df, ratings_df, book_tags_df, tags_df):
    print("\n--- Data Preparation ---")
    books_with_tags = pd.merge(
        books_df, 
        book_tags_df, 
        left_on='book_id', 
        right_on='goodreads_book_id', 
        how='left'
    )
    books_with_tags = pd.merge(books_with_tags, tags_df, on='tag_id', how='left')
    books_content_df = books_with_tags[['book_id', 'title', 'authors', 'tag_name']].copy()
    books_content_df = books_content_df.groupby(['book_id', 'title', 'authors'])['tag_name'].apply(lambda x: " ".join(x.dropna().unique())).reset_index()
    books_content_df.rename(columns={'tag_name': 'tags'}, inplace=True)
    books_content_df['tags'].fillna('', inplace=True)

    ratings_filtered_df = ratings_df[ratings_df['book_id'].isin(books_df['book_id'])].copy()
    ratings_filtered_df.drop_duplicates(subset=['user_id', 'book_id'], inplace=True)
    books_content_df.drop_duplicates(subset=['book_id'], inplace=True)

    books_content_df['content_features'] = books_content_df['title'].fillna('') + " " + \
                                          books_content_df['authors'].fillna('') + " " + \
                                          books_content_df['tags'].fillna('')
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(books_content_df['content_features'])

    user_encoder = LabelEncoder()
    book_encoder = LabelEncoder()
    ratings_filtered_df['user_id_encoded'] = user_encoder.fit_transform(ratings_filtered_df['user_id'])
    ratings_filtered_df['book_id_encoded'] = book_encoder.fit_transform(ratings_filtered_df['book_id'])

    print("Data Preparation Complete.")
    return books_content_df, ratings_filtered_df, tfidf_matrix, user_encoder, book_encoder

def get_content_based_recommendations(book_id, cosine_sim_matrix, df, book_id_to_idx, N=10):
    if book_id not in book_id_to_idx:
        return pd.DataFrame()
    idx = book_id_to_idx[book_id]
    sim_scores = list(enumerate(cosine_sim_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:N+1]
    book_indices = [i[0] for i in sim_scores]
    similar_scores = [i[1] for i in sim_scores]
    recommended_books = df.iloc[book_indices].copy()
    recommended_books['similarity_score'] = similar_scores
    return recommended_books[['title', 'authors', 'similarity_score']]

def get_lightfm_recommendations(user_id, model, user_encoder, book_encoder, books_df, n_items, n_recommendations=10):
    if user_id not in user_encoder.classes_:
        return pd.DataFrame()
    encoded_user_id = user_encoder.transform([user_id])[0]
    scores = model.predict(np.repeat(encoded_user_id, n_items), np.arange(n_items))
    top_items = np.argsort(-scores)[:n_recommendations]
    book_id_decoded = book_encoder.inverse_transform(top_items)
    recommended_books_info = books_df[books_df['book_id'].isin(book_id_decoded)]
    return recommended_books_info[['title', 'authors']].head(n_recommendations)

def main():
    data = load_data()
    if data is None:
        return
    books_df, ratings_df, book_tags_df, tags_df = data

    # Exploratory Data Analysis
    if not os.path.exists('images'):
        os.makedirs('images')
    eda(books_df, ratings_df, book_tags_df, tags_df)

    # Data Preparation
    books_content_df, ratings_filtered_df, tfidf_matrix, user_encoder, book_encoder = data_preparation(
        books_df, ratings_df, book_tags_df, tags_df
    )

    # Modeling: Content-based Filtering
    print("\n--- Modeling: Content-based Filtering ---")
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    book_id_to_idx = pd.Series(books_content_df.index, index=books_content_df['book_id']).drop_duplicates()
    train_df, test_df = train_test_split(ratings_filtered_df, test_size=0.2, random_state=42)

    # Modeling: Collaborative Filtering (LightFM)
    n_users = ratings_filtered_df['user_id_encoded'].nunique()
    n_items = ratings_filtered_df['book_id_encoded'].nunique()
    interaction_matrix = sparse.coo_matrix(
        (ratings_filtered_df['rating'], (ratings_filtered_df['user_id_encoded'], ratings_filtered_df['book_id_encoded'])),
        shape=(n_users, n_items)
    )
    model = LightFM(no_components=20, loss='warp')
    model.fit(interaction_matrix, epochs=10, num_threads=2)

    # Contoh rekomendasi Content-based
    example_book_id = books_content_df['book_id'].sample(1).iloc[0]
    example_book_title = books_content_df[books_content_df['book_id'] == example_book_id]['title'].iloc[0]
    print(f"\n--- Content-based Recommendations for: '{example_book_title}' (ID: {example_book_id}) ---")
    content_recs = get_content_based_recommendations(example_book_id, cosine_sim, books_content_df, book_id_to_idx, N=10)
    print(content_recs)

    # Contoh rekomendasi Collaborative Filtering
    example_user_id = ratings_filtered_df['user_id'].sample(1).iloc[0]
    print(f"\n--- Collaborative Filtering Recommendations for User ID: {example_user_id} ---")
    collab_recs = get_lightfm_recommendations(example_user_id, model, user_encoder, book_encoder, books_df, n_items, n_recommendations=10)
    print(collab_recs)

    # Evaluation
    print("\n--- Evaluation ---")
    print("Evaluasi Content-based Filtering:")
    print(content_recs)

    train_precision = precision_at_k(model, interaction_matrix, k=10).mean()
    train_recall = recall_at_k(model, interaction_matrix, k=10).mean()
    print(f"Precision@10 (train): {train_precision:.4f}")
    print(f"Recall@10 (train): {train_recall:.4f}")

if __name__ == "__main__":
    main()