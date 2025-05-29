import csv
import os
from django.core.management.base import BaseCommand
from lms_app.models import Book, Author, Publisher, Genre

class Command(BaseCommand):
    help = 'Import data from CSV files'

    def handle(self, *args, **options):
        # Get the path to the data directory
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
        
        # Import Authors
        authors_file = os.path.join(data_dir, 'Author.csv')
        if os.path.exists(authors_file):
            with open(authors_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Author.objects.get_or_create(
                        author_id=row['Author_ID'],
                        defaults={
                            'name': row['Name'],
                            'dob': row.get('DOB'),
                            'nationality': row.get('Nationality')
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported authors'))

        # Import Publishers
        publishers_file = os.path.join(data_dir, 'Publisher.csv')
        if os.path.exists(publishers_file):
            with open(publishers_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Publisher.objects.get_or_create(
                        publisher_id=row['Publisher_ID'],
                        defaults={
                            'name': row['Name'],
                            'address': row.get('Address'),
                            'contact_info': row.get('Contact_Info')
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported publishers'))

        # Import Genres
        genres_file = os.path.join(data_dir, 'Genre.csv')
        if os.path.exists(genres_file):
            with open(genres_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    Genre.objects.get_or_create(
                        genre_id=row['Genre_ID'],
                        defaults={
                            'genre_name': row['Genre_Name']
                        }
                    )
            self.stdout.write(self.style.SUCCESS('Successfully imported genres'))

        # Import Books
        books_file = os.path.join(data_dir, 'Book.csv')
        if os.path.exists(books_file):
            with open(books_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        author = Author.objects.get(author_id=row['Author_ID'])
                        genre = Genre.objects.get(genre_id=row['Genre_ID'])
                        
                        Book.objects.get_or_create(
                            book_id=row['Book_ID'],
                            defaults={
                                'title': row['Title'],
                                'year_of_publication': int(row['Year_of_Publication']),
                                'total_copies': int(row['Total_Copies']),
                                'available_copies': int(row['Available_Copies']),
                                'author_id': author,
                                'genre_id': genre,
                                'publisher': row['Publisher'],
                                'rating': float(row['Rating'])
                            }
                        )
                    except (ValueError, KeyError) as e:
                        self.stdout.write(self.style.WARNING(f'Error importing book {row.get("Book_ID", "unknown")}: {str(e)}'))
            self.stdout.write(self.style.SUCCESS('Successfully imported books'))