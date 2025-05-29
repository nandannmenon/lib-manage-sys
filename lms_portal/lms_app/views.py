from operator import index

from django.db import models
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import csv
import os
from django.http import HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import messages
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
import pandas as pd


def home(request):
    return render(request, 'home.html', context={"current_tab":"home"})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Read members data
        members_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'))
        
        # Check credentials
        authenticated = False
        for _, member in members_df.iterrows():
            first_name = member['Name'].split()[0]  # Get first name
            if first_name.lower() == username.lower() and str(member['Member_ID']) == password:
                # Store member details in session
                request.session['member_id'] = member['Member_ID']
                request.session['member_name'] = member['Name']
                authenticated = True
                break
        
        if authenticated:
            return redirect('welcome')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
            return redirect('login')
    
    return render(request, 'login.html')

def welcome(request):
    # Get member details from session
    member_name = request.session.get('member_name', '')
    member_id = request.session.get('member_id', '')
    
    if not member_name:
        return redirect('login')
    
    # Read membership data
    membership_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Membership.csv'))
    member_membership = membership_df[membership_df['Member_ID'] == int(member_id)].iloc[0].to_dict() if not membership_df[membership_df['Member_ID'] == int(member_id)].empty else None
    
    return render(request, 'welcome.html', context={
        "current_tab": "welcome",
        "member_name": member_name,
        "member_id": member_id,
        "membership": member_membership
    })

def book_collection(request):
    # Read books data
    books_data = []
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Book.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            books_data.append(row)

    # Read authors data
    authors_data = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Author.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            authors_data[row['Author_ID']] = row

    # Read genres data
    genres_data = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Genre.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            genres_data[row['Genre_ID']] = row

    # Combine books with their authors and genres
    for book in books_data:
        author_id = book['Author_ID']
        genre_id = book['Genre_ID']
        book['Author'] = authors_data.get(author_id, {'Name': 'Unknown Author'})
        book['Genre'] = genres_data.get(genre_id, {'Genre_Name': 'Unknown Genre'})

    # Prepare genres for the categories section
    genres = list(genres_data.values())

    return render(request, 'books.html', {
        "current_tab": "books",
        "books": books_data,
        "genres": genres
    })

def about(request):
    return render(request, 'about.html', context={"current_tab":"about"})

def admin_dashboard(request):
    if not request.session.get('employee_id'):
        return redirect('login')

    try:
        # Read books data
        books_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'))
        books = books_df.to_dict('records')
        total_books = len(books)
        
        # Read members data
        members_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'))
        members = members_df.to_dict('records')
        total_users = len(members)
        
        # Read authors data
        authors_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Author.csv'))
        authors_dict = authors_df.set_index('Author_ID').to_dict('index')
        
        # Read genres data
        genres_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Genre.csv'))
        genres = genres_df.to_dict('records')
        
        # Read book issues data
        book_issues_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'))
        
        # Read fines data
        fines_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Fine.csv'))
        
        # Get current date
        current_date = datetime.now().date()
        
        # Get overdue books (where return_date is NULL and due_date has passed)
        overdue_books = book_issues_df[
            (book_issues_df['Return_Date'].isna()) & 
            (pd.to_datetime(book_issues_df['Due_Date']).dt.date < current_date)
        ].copy()
        
        total_overdue = len(overdue_books)
        
        # Add book and member details to overdue books
        overdue_books_with_details = []
        for _, issue in overdue_books.iterrows():
            book = books_df[books_df['Book_ID'] == issue['Book_ID']].iloc[0]
            member = members_df[members_df['Member_ID'] == issue['Member_ID']].iloc[0]
            
            # Calculate fine
            due_date = datetime.strptime(issue['Due_Date'], '%Y-%m-%d')
            days_late = (current_date - due_date.date()).days
            fine_amount = max(0, days_late * 1.00)  # Rs 1 per day
            
            # Check if fine exists and its status
            fine_record = fines_df[fines_df['Issue_ID'] == issue['Issue_ID']]
            fine_status = 'Unpaid'
            if not fine_record.empty:
                fine_status = fine_record.iloc[0]['Status']
            
            overdue_books_with_details.append({
                'Book_ID': book['Book_ID'],
                'Title': book['Title'],
                'Member_ID': member['Member_ID'],
                'Member_Name': member['Name'],
                'Issue_Date': issue['Issue_Date'],
                'Due_Date': issue['Due_Date'],
                'Fine_Amount': f"Rs {fine_amount:.2f}",
                'Fine_Status': fine_status
            })
        
        # Combine books with their authors
        for book in books:
            author_id = book['Author_ID']
            book['Author'] = authors_dict.get(author_id, {'Name': 'Unknown Author'})
        
        return render(request, 'admin_dashboard.html', {
            'total_books': total_books,
            'total_users': total_users,
            'total_overdue': total_overdue,
            'books': books,
            'members': members,
            'authors': authors_df.to_dict('records'),
            'genres': genres,
            'overdue_books': overdue_books_with_details
        })
    except Exception:
        return redirect('admin_login')

def add_user(request):
    if not request.session.get('employee_id'):
        return redirect('admin_login')
        
    if request.method == 'POST':
        try:
            # Read existing members
            members_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'))
            
            # Generate new Member_ID
            new_member_id = str(int(members_df['Member_ID'].max()) + 1)
            
            # Create new member record
            new_member = pd.DataFrame([{
                'Member_ID': new_member_id,
                'Name': request.POST['name'],
                'Email': request.POST['email'],
                'Phone_No': request.POST['phone_no'],
                'Address': request.POST['address']
            }])
            
            # Concatenate new member to DataFrame
            members_df = pd.concat([members_df, new_member], ignore_index=True)
            
            # Save updated Member.csv
            members_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'), index=False)
            
            # Handle membership data
            membership_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Membership.csv'))
            
            # Generate new Membership_ID
            new_membership_id = str(int(membership_df['Membership_ID'].max()) + 1)
            
            # Calculate membership dates (4 years from current date)
            current_date = datetime.now()
            end_date = current_date + timedelta(days=4*365)
            
            # Create new membership record
            new_membership = pd.DataFrame([{
                'Membership_ID': new_membership_id,
                'Member_ID': new_member_id,
                'Membership_Type': request.POST['membership_type'],
                'Start_Date': current_date.strftime('%Y-%m-%d'),
                'End_Date': end_date.strftime('%Y-%m-%d')
            }])
            
            # Concatenate new membership to DataFrame
            membership_df = pd.concat([membership_df, new_membership], ignore_index=True)
            
            # Save updated Membership.csv
            membership_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Membership.csv'), index=False)
            
            messages.success(request, 'User added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding user: {str(e)}')
    
    return redirect('admin_dashboard')

def edit_user(request):
    if not request.session.get('employee_id'):
        return redirect('admin_login')
        
    if request.method == 'POST':
        try:
            # Read existing members
            members_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'))
            
            # Update member record
            member_id = request.POST['member_id']
            members_df.loc[members_df['Member_ID'] == member_id, 'Name'] = request.POST['name']
            members_df.loc[members_df['Member_ID'] == member_id, 'Email'] = request.POST['email']
            members_df.loc[members_df['Member_ID'] == member_id, 'Phone_No'] = request.POST['phone_no']
            members_df.loc[members_df['Member_ID'] == member_id, 'Address'] = request.POST['address']
            
            # Save updated DataFrame
            members_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'), index=False)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            messages.success(request, 'User updated successfully!')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Error updating user: {str(e)}')
    
    return redirect('admin_dashboard')

def delete_user(request):
    if request.method == 'POST':
        try:
            # Read existing members
            members_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'))
            
            # Remove member record
            member_id = request.POST['member_id']
            members_df = members_df[members_df['Member_ID'] != member_id]
            
            # Save updated DataFrame
            members_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'), index=False)
            
        except Exception:
            pass
    
    return redirect('admin_dashboard')

def add_book(request):
    if not request.session.get('employee_id'):
        return redirect('admin_login')
        
    if request.method == 'POST':
        try:
            # Read existing books
            books_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'))
            
            # Generate new Book_ID
            new_book_id = str(int(books_df['Book_ID'].max()) + 1)
            
            # Create new book record
            new_book = pd.DataFrame([{
                'Book_ID': new_book_id,
                'Title': request.POST['title'],
                'Year_of_Publication': request.POST['year'],
                'Available_Copies': request.POST['copies'],
                'Total_Copies': request.POST['copies'],
                'Author_ID': request.POST['author_id'],
                'Genre_ID': request.POST['genre_id'],
                'Publisher': request.POST['publisher'],
                'Rating': request.POST.get('rating', 0.0)
            }])
            
            # Concatenate new book to DataFrame
            books_df = pd.concat([books_df, new_book], ignore_index=True)
            
            # Save updated DataFrame
            books_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), index=False)
            
            messages.success(request, 'Book added successfully!')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')
        
        return redirect('admin_dashboard')

def edit_book(request):
    if not request.session.get('employee_id'):
        return redirect('admin_login')
        
    if request.method == 'POST':
        try:
            # Read existing books
            books_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'))
            
            # Update book record
            book_id = request.POST['book_id']
            books_df.loc[books_df['Book_ID'] == book_id, 'Title'] = request.POST['title']
            books_df.loc[books_df['Book_ID'] == book_id, 'Year_of_Publication'] = request.POST['year']
            books_df.loc[books_df['Book_ID'] == book_id, 'Total_Copies'] = request.POST['copies']
            books_df.loc[books_df['Book_ID'] == book_id, 'Author_ID'] = request.POST['author_id']
            books_df.loc[books_df['Book_ID'] == book_id, 'Genre_ID'] = request.POST['genre_id']
            books_df.loc[books_df['Book_ID'] == book_id, 'Publisher'] = request.POST['publisher']
            books_df.loc[books_df['Book_ID'] == book_id, 'Rating'] = request.POST.get('rating', 0.0)
            
            # Save updated DataFrame
            books_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), index=False)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            messages.success(request, 'Book updated successfully!')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            messages.error(request, f'Error updating book: {str(e)}')
    
    return redirect('admin_dashboard')

def delete_book(request):
    if request.method == 'POST':
        try:
            # Read existing books
            books_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'))
            
            # Remove book record
            book_id = request.POST['book_id']
            books_df = books_df[books_df['Book_ID'] != book_id]
            
            # Save updated DataFrame
            books_df.to_csv(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), index=False)
            
        except Exception:
            pass
    
    return redirect('admin_dashboard')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Read Employee.csv to verify credentials
        employee_file = os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Employee.csv')
        with open(employee_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['Username'] == username and row['Password'] == password:
                    # Store employee details in session
                    request.session['employee_id'] = row['Employee_ID']
                    request.session['employee_name'] = row['Name']
        return redirect('admin')
        
        return redirect('admin_login')
    
    return render(request, 'admin_login.html')

def books(request):
    # Read books data
    books_data = []
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Book.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            books_data.append(row)

    # Read authors data
    authors_data = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Author.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            authors_data[row['Author_ID']] = row

    # Read genres data
    genres_data = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Genre.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            genres_data[row['Genre_ID']] = row

    # Read book issues data
    book_issues = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Book_Issue.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['Book_ID'] not in book_issues:
                book_issues[row['Book_ID']] = []
            book_issues[row['Book_ID']].append(row)

    # Read members data
    members_data = {}
    with open(os.path.join(os.path.dirname(__file__), 'data', 'Member.csv'), 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            members_data[row['Member_ID']] = row

    # Prepare books data with borrowing history
    books_with_history = []
    for book in books_data:
        author_id = book['Author_ID']
        genre_id = book['Genre_ID']
        book['Author'] = authors_data.get(author_id, {'Name': 'Unknown Author'})
        book['Genre'] = genres_data.get(genre_id, {'Genre_Name': 'Unknown Genre'})
        
        # Add borrowing history
        borrowing_history = []
        if book['Book_ID'] in book_issues:
            for issue in book_issues[book['Book_ID']]:
                member = members_data.get(issue['Member_ID'], {'Name': 'Unknown Member'})
                borrowing_history.append({
                    'member_name': member['Name'],
                    'issue_date': issue['Issue_Date'],
                    'due_date': issue['Due_Date'],
                    'return_date': issue['Return_Date'] if issue['Return_Date'] != 'NULL' else 'Not Returned'
                })
        
        books_with_history.append({
            'Book_ID': book['Book_ID'],
            'Title': book['Title'],
            'borrowing_history': borrowing_history
        })

    # Prepare genres for the categories section
    genres = list(genres_data.values())

    return render(request, 'books.html', {
        "current_tab": "books",
        "books": books_data,
        "genres": genres,
        "books_json": json.dumps(books_with_history)
    })

def calculate_fine(issue_date, due_date, return_date=None):
    try:
        due = datetime.strptime(due_date, '%Y-%m-%d')
        if return_date and return_date != 'NULL':
            ret = datetime.strptime(return_date, '%Y-%m-%d')
            days_late = (ret - due).days
        else:
            current_date = datetime.now()
            days_late = (current_date - due).days
        
        if days_late > 15:
            return days_late * 1.00  # Rs 1 per day after 15 days
        return 0.00
    except Exception as e:
        print(f"Error calculating fine: {str(e)}")
        return 0.00

def update_fines():
    try:
        # Read Book_Issue.csv
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'), 'r') as file:
            reader = csv.DictReader(file)
            book_issues = list(reader)

        # Read existing fines
        fine_file = os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Fine.csv')
        existing_fines = set()
        if os.path.exists(fine_file):
            with open(fine_file, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    existing_fines.add(row['Issue_ID'])

        # Calculate fines for overdue books
        new_fines = []
        for issue in book_issues:
            if issue['Issue_ID'] not in existing_fines:
                fine_amount = calculate_fine(issue['Issue_Date'], issue['Due_Date'], issue['Return_Date'])
                if fine_amount > 0:
                    new_fines.append({
                        'Issue_ID': issue['Issue_ID'],
                        'Member_ID': issue['Member_ID'],
                        'Book_ID': issue['Book_ID'],
                        'Amount': f"{fine_amount:.2f}",
                        'Status': 'Pending',
                        'Payment_Date': 'NULL'
                    })

        # Append new fines to Fine.csv
        if new_fines:
            fieldnames = ['Issue_ID', 'Member_ID', 'Book_ID', 'Amount', 'Status', 'Payment_Date']
            file_exists = os.path.exists(fine_file)
            
            with open(fine_file, 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_fines)

    except Exception as e:
        print(f"Error updating fines: {str(e)}")

def checkout_book(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')
        member_id = request.session.get('member_id')
        issue_date = request.POST.get('issue_date')
        due_date = request.POST.get('due_date')

        if not member_id:
            messages.error(request, 'Please login to checkout books.')
            return redirect('login')

        try:
            # Read Book.csv
            book_file = os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv')
            books_df = pd.read_csv(book_file, dtype={'Book_ID': str, 'Title': str})
            
            # Find the book
            book_row = books_df[books_df['Book_ID'] == book_id]
            if book_row.empty:
                messages.error(request, 'Book not found.')
                return redirect('books')
                
            book_title = book_row.iloc[0]['Title']
            available_copies = int(book_row.iloc[0]['Available_Copies'])
            
            if available_copies <= 0:
                messages.error(request, f'Sorry, "{book_title}" is currently not available for checkout.')
                return redirect('books')
            
            # Update available copies
            books_df.loc[books_df['Book_ID'] == book_id, 'Available_Copies'] = available_copies - 1
            
            # Save updated Book.csv
            books_df.to_csv(book_file, index=False)

            # Add new book issue record
            book_issue_file = os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv')
            
            # Get next Issue_ID
            if os.path.exists(book_issue_file):
                issues_df = pd.read_csv(book_issue_file, dtype={'Issue_ID': str, 'Member_ID': str, 'Book_ID': str})
                issue_id = str(len(issues_df) + 1)
            else:
                issue_id = '1'
                issues_df = pd.DataFrame(columns=['Issue_ID', 'Member_ID', 'Book_ID', 'Employee_ID', 'Issue_Date', 'Due_Date', 'Return_Date'])

            # Create new issue record
            new_issue = pd.DataFrame([{
                'Issue_ID': issue_id,
                'Member_ID': member_id,
                'Book_ID': book_id,
                'Employee_ID': '401',  # Default employee ID
                'Issue_Date': issue_date,
                'Due_Date': due_date,
                'Return_Date': 'NULL'
            }])

            # Append new issue
            issues_df = pd.concat([issues_df, new_issue], ignore_index=True)
            issues_df.to_csv(book_issue_file, index=False)

            # Check and update fines
            update_fines()
            
            messages.success(request, f'Successfully checked out "{book_title}". Due date: {due_date}')
            
        except Exception as e:
            messages.error(request, 'An error occurred while checking out the book. Please try again.')
            
        return redirect('books')
    
    return redirect('books')

def get_current_borrowings(request, member_id):
    try:
        current_borrowings = []
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Member_ID'] == str(member_id) and row['Return_Date'] == 'NULL':
                    # Get book title
                    with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), 'r') as book_file:
                        book_reader = csv.DictReader(book_file)
                        for book in book_reader:
                            if book['Book_ID'] == row['Book_ID']:
                                current_borrowings.append({
                                    'title': book['Title'],
                                    'issue_date': row['Issue_Date'],
                                    'due_date': row['Due_Date']
                                })
                                break
        return JsonResponse(current_borrowings, safe=False)
    except Exception as e:
        print(f"Error in get_current_borrowings: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_borrowing_history(request, member_id):
    try:
        borrowing_history = []
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Member_ID'] == str(member_id):
                    # Get book title
                    with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), 'r') as book_file:
                        book_reader = csv.DictReader(book_file)
                        for book in book_reader:
                            if book['Book_ID'] == row['Book_ID']:
                                borrowing_history.append({
                                    'title': book['Title'],
                                    'issue_date': row['Issue_Date'],
                                    'due_date': row['Due_Date'],
                                    'return_date': row['Return_Date'] if row['Return_Date'] != 'NULL' else 'Not Returned'
                                })
                                break
        return JsonResponse(borrowing_history, safe=False)
    except Exception as e:
        print(f"Error in get_borrowing_history: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_pending_charges(request, member_id):
    try:
        pending_charges = []
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Member_ID'] == str(member_id):
                    # Get book title
                    with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book.csv'), 'r') as book_file:
                        book_reader = csv.DictReader(book_file)
                        for book in book_reader:
                            if book['Book_ID'] == row['Book_ID']:
                                due_date = datetime.strptime(row['Due_Date'], '%Y-%m-%d')
                                return_date = datetime.strptime(row['Return_Date'], '%Y-%m-%d') if row['Return_Date'] != 'NULL' else None
                                
                                if return_date and return_date > due_date:
                                    # Calculate fine (assuming Rs 1 per day late)
                                    days_late = (return_date - due_date).days
                                    amount = days_late * 1.00
                                    
                                    pending_charges.append({
                                        'book_title': book['Title'],
                                        'due_date': row['Due_Date'],
                                        'return_date': row['Return_Date'],
                                        'amount': f"{amount:.2f}"
                                    })
                                break
        return JsonResponse(pending_charges, safe=False)
    except Exception as e:
        print(f"Error in get_pending_charges: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def get_member_name(member_id):
    try:
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Member.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Member_ID'] == str(member_id):
                    return row['Name']  # Using the 'Name' field directly from Member.csv
        return 'Unknown Member'
    except Exception as e:
        print(f"Error getting member name: {str(e)}")
        return 'Unknown Member'

@api_view(['GET'])
def book_history(request, book_id):
    try:
        # Read Book_Issue.csv
        book_issues = []
        with open(os.path.join(settings.BASE_DIR, 'lms_app', 'data', 'Book_Issue.csv'), 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Book_ID'] == str(book_id):
                    # Get member name from Member.csv
                    member_name = get_member_name(row['Member_ID'])
                    book_issues.append({
                        'member_name': member_name,
                        'issue_date': row['Issue_Date'],
                        'due_date': row['Due_Date'],
                        'return_date': row['Return_Date']
                    })
        
        return JsonResponse(book_issues, safe=False)
    except Exception as e:
        print(f"Error in book_history: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

