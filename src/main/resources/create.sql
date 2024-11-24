CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Reservations (
    ID int,
    PatientName varchar(255) REFERENCES Patients (Username),
    CaregiverName varchar(255) REFERENCES Caregivers (Username),
    VaccineName varchar(255) REFERENCES Vaccines (Name),
    Time date,
    PRIMARY KEY (ID)
);