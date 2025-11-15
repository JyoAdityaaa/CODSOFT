import tkinter as tk
from tkinter import ttk
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

# -----------------------------------
# Load CSV files
# -----------------------------------
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

movies["title"] = movies["title"].astype(str)
movies["genres"] = movies["genres"].astype(str)

# -----------------------------------
# CONTENT-BASED FILTERING
# -----------------------------------
def recommend_content_based(movie_title, top_n=5):
    cv = CountVectorizer(tokenizer=lambda x: x.split("|"))
    genre_matrix = cv.fit_transform(movies["genres"])
    similarity = cosine_similarity(genre_matrix)

    if movie_title not in movies["title"].values:
        return ["Movie not found"]

    idx = movies[movies["title"] == movie_title].index[0]

    scores = list(enumerate(similarity[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    # recommended indices (skip self)
    recommended_indices = [i[0] for i in scores if i[0] != idx][:top_n]

    # final list
    results = movies['title'].iloc[recommended_indices].tolist()

    # EXTRA SAFETY FILTER (remove exact same movie if somehow repeated)
    results = [m for m in results if m != movie_title]

    return results


# -----------------------------------
# COLLABORATIVE FILTERING
# -----------------------------------
def recommend_collaborative(user_id, top_n=5):
    user_movie = ratings.pivot_table(
        index="userId",
        columns="movieId",
        values="rating"
    ).fillna(0)

    if user_id not in user_movie.index:
        return ["User not found"]

    similarity = cosine_similarity(user_movie)
    sim_df = pd.DataFrame(similarity, index=user_movie.index, columns=user_movie.index)

    similar_user = sim_df[user_id].sort_values(ascending=False).index[1]

    similar_user_ratings = ratings[ratings["userId"] == similar_user]
    user_movies = ratings[ratings["userId"] == user_id]["movieId"].tolist()

    recommendations = similar_user_ratings[
        ~similar_user_ratings["movieId"].isin(user_movies)
    ].sort_values(by="rating", ascending=False).head(top_n)

    final = movies[movies["movieId"].isin(recommendations["movieId"])]["title"].tolist()

    # EXTRA: Remove duplicates or mistakes
    final = list(dict.fromkeys(final))

    return final


# -----------------------------------
# GUI APPLICATION (Tkinter)
# -----------------------------------

root = tk.Tk()
root.title("Simple Movie Recommendation System")
root.geometry("600x500")
root.resizable(False, False)

# Title
title_label = tk.Label(root, text="Movie Recommendation System", font=("Arial", 18, "bold"))
title_label.pack(pady=10)

# Notebook Tabs
tab_parent = ttk.Notebook(root)
tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="Content-Based")
tab_parent.add(tab2, text="Collaborative")
tab_parent.pack(expand=1, fill="both")

# -----------------------------------
# TAB 1: CONTENT-BASED
# -----------------------------------
label1 = tk.Label(tab1, text="Select a Movie:", font=("Arial", 12))
label1.pack(pady=10)
label2 = tk.Label(tab1, text="Please click on the dropdown to choose movies", font=("Arial", 8))
label2.pack(pady=10)

movie_var = tk.StringVar()
movie_dropdown = ttk.Combobox(tab1, textvariable=movie_var, values=list(movies["title"]), width=50)
movie_dropdown.pack()

output_box1 = tk.Text(tab1, height=10, width=60)
output_box1.pack(pady=10)

def show_content_recommendations():
    output_box1.delete(1.0, tk.END)
    movie = movie_var.get()
    recs = recommend_content_based(movie)
    output_box1.insert(tk.END, "Recommendations:\n\n")
    for r in recs:
        output_box1.insert(tk.END, f"• {r}\n")

tk.Button(tab1, text="Recommend", command=show_content_recommendations).pack(pady=5)

# -----------------------------------
# TAB 2: COLLABORATIVE
# -----------------------------------
label2 = tk.Label(tab2, text="Select User ID:", font=("Arial", 12))
label2.pack(pady=10)

user_var = tk.IntVar()
user_dropdown = ttk.Combobox(tab2, textvariable=user_var, values=sorted(ratings["userId"].unique()), width=20)
user_dropdown.pack()

output_box2 = tk.Text(tab2, height=10, width=60)
output_box2.pack(pady=10)

def show_collab_recommendations():
    output_box2.delete(1.0, tk.END)
    user = user_var.get()
    recs = recommend_collaborative(user)
    output_box2.insert(tk.END, "Recommendations:\n\n")
    for r in recs:
        output_box2.insert(tk.END, f"• {r}\n")

tk.Button(tab2, text="Recommend", command=show_collab_recommendations).pack(pady=5)

# -----------------------------------
# RUN THE APP
# -----------------------------------
root.mainloop()
