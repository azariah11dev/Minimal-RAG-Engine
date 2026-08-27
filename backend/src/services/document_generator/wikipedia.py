import os
import wikipedia

wikipedia.set_lang("en")

articles = ["OpenAI", "Microsoft"]

def main():
    base_dir = os.path.join(
        os.path.dirname(__file__),
        "..", "..", "..",
        "documents",
        "test_documents"
    )

    os.makedirs(base_dir, exist_ok=True)

    for article in articles:
        try:
            print(f"Downloading article: {article}")
            content = wikipedia.page(article).content

            file_path = os.path.join(base_dir, f"{article}.txt")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Saved: {file_path}")

        except wikipedia.exceptions.DisambiguationError as e:
            print(f"Disambiguation for {article}: {e.options}")

        except wikipedia.exceptions.PageError:
            print(f"Page not found: {article}")

        except Exception as e:
            print(f"Error downloading {article}: {e}")

if __name__ == "__main__":
    main()
