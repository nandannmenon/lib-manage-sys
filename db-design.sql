CREATE TABLE Author (
    Author_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    DOB DATE,
    Nationality VARCHAR(100)
) ENGINE=InnoDB;

CREATE TABLE Publisher (
    Publisher_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Address TEXT,
    Contact_Info VARCHAR(15) 
) ENGINE=InnoDB;

CREATE TABLE Genre (
    Genre_ID INT PRIMARY KEY AUTO_INCREMENT,
    Genre_Name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE Member (
    Member_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Phone_No VARCHAR(15),
    Address TEXT
) ENGINE=InnoDB;

CREATE TABLE Membership (
    Membership_ID INT PRIMARY KEY AUTO_INCREMENT,
    Member_ID INT NOT NULL,
    Membership_Type ENUM('Standard', 'Premium') NOT NULL, 
    Start_Date DATE NOT NULL,
    End_Date DATE,
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Employee (
    Employee_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Password VARCHAR(255) NOT NULL,
    Phone_No VARCHAR(15)
) ENGINE=InnoDB;

CREATE TABLE Book (
    Book_ID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(255) NOT NULL,
    Year_of_Publication YEAR,
    Total_Copies INT NOT NULL CHECK (Total_Copies >= 0),
    Available_Copies INT NOT NULL CHECK (Available_Copies >= 0),
    Author_ID INT,
    Genre_ID INT,
    Publisher_ID INT,
    FOREIGN KEY (Author_ID) REFERENCES Author(Author_ID) ON DELETE SET NULL,
    FOREIGN KEY (Genre_ID) REFERENCES Genre(Genre_ID) ON DELETE SET NULL,
    FOREIGN KEY (Publisher_ID) REFERENCES Publisher(Publisher_ID) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE Book_Issue (
    Issue_ID INT PRIMARY KEY AUTO_INCREMENT,
    Member_ID INT NOT NULL,
    Book_ID INT NOT NULL,
    Employee_ID INT,
    Issue_Date DATE NOT NULL,
    Due_Date DATE NOT NULL,
    Return_Date DATE DEFAULT NULL,
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES Book(Book_ID) ON DELETE CASCADE,
    FOREIGN KEY (Employee_ID) REFERENCES Employee(Employee_ID) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE TABLE Review (
    Review_ID INT PRIMARY KEY AUTO_INCREMENT,
    Member_ID INT NOT NULL,
    Book_ID INT NOT NULL,
    Review_Text TEXT,
    Rating INT CHECK (Rating BETWEEN 1 AND 5),
    Date DATE,
    FOREIGN KEY (Member_ID) REFERENCES Member(Member_ID) ON DELETE CASCADE,
    FOREIGN KEY (Book_ID) REFERENCES Book(Book_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Fine (
    Fine_ID INT PRIMARY KEY AUTO_INCREMENT,
    Issue_ID INT NOT NULL,
    Amount DECIMAL(10,2) NOT NULL CHECK (Amount >= 0),
    Status ENUM('Paid', 'Unpaid') DEFAULT 'Unpaid',
    Payment_Date DATE,
    FOREIGN KEY (Issue_ID) REFERENCES Book_Issue(Issue_ID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Transaction (
    Transaction_ID INT PRIMARY KEY AUTO_INCREMENT,
    Membership_ID INT DEFAULT NULL,
    Fine_ID INT DEFAULT NULL,
    Payment_Amount DECIMAL(10,2) NOT NULL CHECK (Payment_Amount >= 0),
    Payment_Method ENUM('Cash', 'Card', 'Online') NOT NULL,
    Payment_Date DATE NOT NULL,
    FOREIGN KEY (Membership_ID) REFERENCES Membership(Membership_ID) ON DELETE CASCADE,
    FOREIGN KEY (Fine_ID) REFERENCES Fine(Fine_ID) ON DELETE CASCADE
) ENGINE=InnoDB;