-- =========================================================================
-- AI-Powered Multilingual Smart Campus Navigation System (MLACW)
-- Maharani Lakshmi Ammanni College for Women (Autonomous), Malleswaram
-- Relational Database Schema & Seed Data (database.sql)
-- =========================================================================

-- 1. Locations Table (Topological Nodes)
CREATE TABLE IF NOT EXISTS campus_locations (
    location_id VARCHAR(20) PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    kannada_name VARCHAR(150),
    hindi_name VARCHAR(150),
    category VARCHAR(50) NOT NULL, -- Entrance, Administration, Academic, Lab, Library, Hall, Food, Sports, Transit
    block VARCHAR(50) NOT NULL,    -- Main Quad, Admin Block, Block A, Block B, Block C, Block D, Block E
    floor INT NOT NULL DEFAULT 0,  -- 0 = Ground, 1, 2, 3
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    is_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    has_elevator_access BOOLEAN NOT NULL DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_locations_floor ON campus_locations(floor);
CREATE INDEX idx_locations_block ON campus_locations(block);
CREATE INDEX idx_locations_coords ON campus_locations(latitude, longitude);

-- 2. Departments Table
CREATE TABLE IF NOT EXISTS departments (
    department_id VARCHAR(20) PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    kannada_name VARCHAR(150),
    hindi_name VARCHAR(150),
    block VARCHAR(50) NOT NULL,
    floor INT NOT NULL,
    location_id VARCHAR(20),
    hod_name VARCHAR(100),
    contact_email VARCHAR(100),
    phone_ext VARCHAR(20),
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE SET NULL
);

-- 3. Classrooms & Laboratories Table
CREATE TABLE IF NOT EXISTS classrooms (
    classroom_id VARCHAR(20) PRIMARY KEY,
    room_number VARCHAR(30) NOT NULL,
    room_name VARCHAR(100) NOT NULL,
    block VARCHAR(50) NOT NULL,
    floor INT NOT NULL,
    capacity INT NOT NULL DEFAULT 40,
    facilities TEXT,
    is_wheelchair_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    department_id VARCHAR(20),
    location_id VARCHAR(20),
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE SET NULL,
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id) ON DELETE CASCADE
);

-- 4. Navigation Paths Table (Topological Edges)
CREATE TABLE IF NOT EXISTS navigation_paths (
    path_id VARCHAR(20) PRIMARY KEY,
    source_node VARCHAR(100) NOT NULL,
    target_node VARCHAR(100) NOT NULL,
    distance_meters INT NOT NULL,
    path_type VARCHAR(50) NOT NULL, -- Corridor, Stairs, Elevator, Ramp, Open Walkway
    is_accessible BOOLEAN NOT NULL DEFAULT TRUE,
    crowd_level VARCHAR(20) NOT NULL DEFAULT 'Low', -- Low, Medium, High
    transition_type VARCHAR(30) NOT NULL DEFAULT 'Horizontal', -- Horizontal, Vertical
    weight DECIMAL(6, 2) GENERATED ALWAYS AS (
        distance_meters * (CASE crowd_level WHEN 'High' THEN 1.8 WHEN 'Medium' THEN 1.3 ELSE 1.0 END)
    ) STORED
);

CREATE INDEX idx_paths_source ON navigation_paths(source_node);
CREATE INDEX idx_paths_target ON navigation_paths(target_node);
CREATE INDEX idx_paths_accessible ON navigation_paths(is_accessible);

-- 5. Students Table
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    roll_number VARCHAR(30) UNIQUE NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    department_id VARCHAR(20),
    program VARCHAR(50) NOT NULL,
    year_of_study INT NOT NULL,
    section VARCHAR(10),
    wheelchair_user BOOLEAN NOT NULL DEFAULT FALSE,
    emergency_contact VARCHAR(25),
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

-- 6. Faculty Table
CREATE TABLE IF NOT EXISTS faculty (
    faculty_id VARCHAR(20) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    designation VARCHAR(100) NOT NULL,
    department_id VARCHAR(20),
    cabin_room VARCHAR(50),
    location_id VARCHAR(20),
    email VARCHAR(100),
    consultation_hours VARCHAR(100),
    FOREIGN KEY (department_id) REFERENCES departments(department_id),
    FOREIGN KEY (location_id) REFERENCES campus_locations(location_id)
);

-- 7. Navigation Logs Table
CREATE TABLE IF NOT EXISTS navigation_logs (
    log_id VARCHAR(20) PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    start_location VARCHAR(100) NOT NULL,
    destination_location VARCHAR(100) NOT NULL,
    language VARCHAR(30) NOT NULL DEFAULT 'English',
    is_wheelchair_mode BOOLEAN NOT NULL DEFAULT FALSE,
    distance_meters INT NOT NULL,
    estimated_time_min DECIMAL(4, 1) NOT NULL,
    path_nodes_count INT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Completed'
);

CREATE INDEX idx_logs_timestamp ON navigation_logs(timestamp);
CREATE INDEX idx_logs_dest ON navigation_logs(destination_location);

-- 8. Multilingual NLP Queries Table
CREATE TABLE IF NOT EXISTS nlp_queries (
    query_id VARCHAR(20) PRIMARY KEY,
    raw_query_text TEXT NOT NULL,
    detected_language VARCHAR(30) NOT NULL,
    intent VARCHAR(50) NOT NULL,
    extracted_entity VARCHAR(100),
    mapped_node VARCHAR(100),
    confidence_score DECIMAL(4, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. Dashboard Space Planning Table
CREATE TABLE IF NOT EXISTS dashboard_data (
    metric_id INT AUTO_INCREMENT PRIMARY KEY,
    metric_category VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value VARCHAR(50) NOT NULL,
    unit VARCHAR(30),
    details TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 10. Useful Views for Institutional Space Analytics
CREATE OR REPLACE VIEW view_popular_destinations AS
SELECT 
    destination_location, 
    COUNT(*) as total_routes_requested, 
    SUM(CASE WHEN is_wheelchair_mode THEN 1 ELSE 0 END) as wheelchair_requests,
    AVG(distance_meters) as avg_walking_distance
FROM navigation_logs
GROUP BY destination_location
ORDER BY total_routes_requested DESC;

CREATE OR REPLACE VIEW view_language_distribution AS
SELECT 
    language, 
    COUNT(*) as queries_count, 
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM navigation_logs), 2) as percentage
FROM navigation_logs
GROUP BY language;


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds


-- =========================================================================
-- AUTHENTIC RELATIONAL SEEDS
-- =========================================================================

-- 11. Campus Locations Seeds
INSERT INTO campus_locations (location_id, location_name, kannada_name, hindi_name, category, block, floor, latitude, longitude, is_accessible, has_elevator_access, description) VALUES
('LOC_001', 'Main Gate', 'ಮುಖ್ಯ ದ್ವಾರ', 'मुख्य द्वार', 'Entrance', 'Campus Entrance', 0, 13.0113500, 77.5687000, TRUE, FALSE, 'Primary college pedestrian and vehicular entrance gate on the main road.'),
('LOC_002', 'Security Cabin', 'ಭದ್ರತಾ ಕೊಠಡಿ', 'सुरक्षा केबिन', 'Security', 'Campus Entrance', 0, 13.0114000, 77.5687100, TRUE, FALSE, 'Campus security cabin and visitor check post inside the main gate facing the college.'),
('LOC_003', 'Administrative Block Foyer', 'ಆಡಳಿತ ಮುಖಮಂಟಪ', 'प्रशासनिक फ़ोयर', 'Administration', 'Admin Block', 0, 13.0114800, 77.5687200, TRUE, TRUE, 'Central ground-floor entrance foyer. Features Founder Director Dr. M. C. Sastri''s bust on the left wall and mLAC reception desk with Ganesha idol straight ahead.'),
('LOC_004', 'Principal Office', 'ಪ್ರಾಂಶುಪಾಲರ ಕಚೇರಿ', 'प्राचार्य कार्यालय', 'Administration', 'Admin Block', 0, 13.0114900, 77.5687600, TRUE, FALSE, 'Office of the College Principal located along the administrative foyer corridor.'),
('LOC_005', 'Vice Principal Office', 'ಉಪಪ್ರಾಂಶುಪಾಲರ ಕಚೇರಿ', 'उप-प्राचार्य कार्यालय', 'Administration', 'Admin Block', 0, 13.0115000, 77.5687800, TRUE, FALSE, 'Office of the Vice Principal in the ground-floor administrative wing.'),
('LOC_006', 'Administrative Office', 'ಆಡಳಿತ ಕಚೇರಿ', 'प्रशासनिक कार्यालय', 'Administration', 'Admin Block', 0, 13.0114700, 77.5687500, TRUE, FALSE, 'Student admissions, fees, and general administration service counter.'),
('LOC_007', 'Medical & First Aid Room', 'ವೈದ್ಯಕೀಯ ಮತ್ತು ಪ್ರಥಮ ಚಿಕಿತ್ಸಾ ಕೊಠಡಿ', 'चिकित्सा और प्राथमिक चिकित्सा कक्ष', 'Medical', 'Admin Block', 0, 13.0114600, 77.5687800, TRUE, FALSE, 'Campus emergency healthcare and first aid facility.'),
('LOC_008', 'Campus Central Elevator', 'ಕಾಲೇಜು ಕೇಂದ್ರೀಯ ಲಿಫ್ಟ್', 'कॉलेज केंद्रीय लिफ्ट', 'Transit', 'Admin Block', 0, 13.0114900, 77.5687000, TRUE, TRUE, 'Accessible passenger elevator in the central building providing barrier-free access across all floors.'),
('LOC_009', 'PU College Stairs', 'ಪಿಯು ಕಾಲೇಜು ಮೆಟ್ಟಿಲುಗಳು', 'पीयू कॉलेज सीढ़ियाँ', 'Transit', 'Left Wing', 0, 13.0115500, 77.5686000, FALSE, FALSE, 'North-west staircase next to Reprography room and Golden Jubilee Seminar Hall leading to upper floors.'),
('LOC_010', 'Reprography Room', 'ರಿಪ್ರೋಗ್ರಫಿ ಕೊಠಡಿ', 'रिप्रोग्राफी कक्ष', 'Facility', 'Left Wing', 0, 13.0115600, 77.5685800, TRUE, FALSE, 'College printing and reprography facility next to PU College stairs.'),
('LOC_011', 'Mushroom Cultivation Lab', 'ಅಣಬೆ ಕೃಷಿ ಪ್ರಯೋಗಾಲಯ', 'मशरूम की खेती प्रयोगशाला', 'Lab', 'Left Wing', 0, 13.0115700, 77.5685700, TRUE, FALSE, 'Botany department specialized mushroom cultivation laboratory.'),
('LOC_012', 'Golden Jubilee Seminar Hall', 'ಸುವರ್ಣ ಮಹೋತ್ಸವ ವಿಚಾರ ಸಂಕಿರಣ ಭವನ', 'स्वर्ण जयंती संगोष्ठी हॉल', 'Hall', 'Left Wing', 0, 13.0115800, 77.5685900, TRUE, FALSE, 'Major college auditorium and seminar hall at the head of the classroom corridor, right by PU College Stairs and Classroom G1.'),
('LOC_013', 'Xerox & Stationery Kiosk', 'ಜೆರಾಕ್ಸ್ ಮತ್ತು ಸ್ಟೇಷನರಿ ಕಿಯೋಸ್ಕ್', 'ज़ेरॉक्स और स्टेशनरी कियोस्क', 'Facility', 'Courtyard', 0, 13.0115400, 77.5686200, TRUE, FALSE, 'Campus stationery and photocopying kiosk in the courtyard area.'),
('LOC_014', 'Classroom G1', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೧', 'कक्षा जी 1', 'Classroom', 'Left Wing', 0, 13.0116000, 77.5685800, TRUE, FALSE, 'Ground floor classroom at the start of the classroom corridor, next to Golden Jubilee Seminar Hall.'),
('LOC_015', 'Classroom G2', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೨', 'कक्षा जी 2', 'Classroom', 'Left Wing', 0, 13.0116300, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G1.'),
('LOC_016', 'Classroom G3', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೩', 'कक्षा जी 3', 'Classroom', 'Left Wing', 0, 13.0116600, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G2.'),
('LOC_017', 'Classroom G4', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೪', 'कक्षा जी 4', 'Classroom', 'Left Wing', 0, 13.0116900, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G3.'),
('LOC_018', 'Classroom G5', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೫', 'कक्षा जी 5', 'Classroom', 'Left Wing', 0, 13.0117200, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G4.'),
('LOC_019', 'Classroom G6', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೬', 'कक्षा जी 6', 'Classroom', 'Left Wing', 0, 13.0117500, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G5.'),
('LOC_020', 'Classroom G7', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೭', 'कक्षा जी 7', 'Classroom', 'Left Wing', 0, 13.0117800, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom directly adjacent to Classroom G6.'),
('LOC_021', 'Classroom G8', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೮', 'कक्षा जी 8', 'Classroom', 'Left Wing', 0, 13.0118100, 77.5685800, TRUE, FALSE, 'Ground floor classroom along the left wing corridor leading to Classroom G9.'),
('LOC_105', 'Classroom G9', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೯', 'कक्षा जी 9', 'Classroom', 'Left Wing', 0, 13.0118300, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom located past Classroom G8 along the left wing corridor.'),
('LOC_106', 'Classroom G10', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೧೦', 'कक्षा जी 10', 'Classroom', 'Left Wing', 0, 13.0118500, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom located along the left wing corridor adjacent to Classroom G9.'),
('LOC_107', 'Classroom G11', 'ತರಗತಿ ಕೊಠಡಿ ಜಿ ೧೧', 'कक्षा जी 11', 'Classroom', 'Left Wing', 0, 13.0118700, 77.5685800, TRUE, FALSE, 'Ground floor lecture classroom at the end of the classroom wing corridor near Controller of Examination and Sports & Gym.'),
('LOC_022', 'Controller of Examination', 'ಪರೀಕ್ಷಾ ನಿಯಂತ್ರಕರ ಕಚೇರಿ', 'परीक्षा नियंत्रक कार्यालय', 'Administration', 'Left Wing', 0, 13.0118300, 77.5686000, TRUE, FALSE, 'Examination administration office located past Classroom G11.'),
('LOC_023', 'Sports & Gym', 'ಕ್ರೀಡೆ ಮತ್ತು ಜಿಮ್', 'खेल और जिम', 'Sports', 'Left Wing', 0, 13.0118400, 77.5686400, TRUE, FALSE, 'Physical education department and campus fitness gym next to Controller of Examination.'),
('LOC_024', 'South Staircase', 'ದಕ್ಷಿಣ ಮೆಟ್ಟಿಲುಗಳು', 'दक्षिणी सीढ़ियाँ', 'Transit', 'South Wing', 0, 13.0118500, 77.5686800, FALSE, FALSE, 'Staircase near Sports & Gym and Girls Washroom connecting ground floor to upper floors south wing.'),
('LOC_025', 'Girls Washroom', 'ವಿದ್ಯಾರ್ಥಿನಿಯರ ಶೌಚಾಲಯ (ನೆಲ ಮಹಡಿ)', 'छात्राओं का शौचालय (भूतल)', 'Facility', 'South Wing', 0, 13.0118500, 77.5687200, TRUE, FALSE, 'Ground floor student restrooms located near South Staircase and Sports & Gym.'),
('LOC_026', 'College Garden Walkway', 'ಕಾಲೇಜು ಉದ್ಯಾನವನ ಮಾರ್ಗ', 'कॉलेज गार्डन वॉकवे', 'Facility', 'Garden Side', 0, 13.0115500, 77.5689000, TRUE, FALSE, 'Paved scenic walkway on the right side of the college connecting the front entrance directly to the Canteen.'),
('LOC_027', 'Canteen Area', 'ಕ್ಯಾಂಟೀನ್ ಆವರಣ', 'कैंटीन परिसर', 'Food', 'Garden Side', 0, 13.0117500, 77.5689000, TRUE, FALSE, 'Spacious campus dining hall and seating area connected to the garden walkway and south wing corridor.'),
('LOC_028', 'Canteen Kitchen', 'ಕ್ಯಾಂಟೀನ್ ಅಡುಗೆ ಕೋಣೆ', 'कैंटीन रसोई', 'Food', 'Garden Side', 0, 13.0117800, 77.5689500, TRUE, FALSE, 'Canteen food preparation area and ordering counter.'),
('LOC_029', 'Parking Area & Ramp', 'ಪಾರ್ಕಿಂಗ್ ಪ್ರದೇಶ ಮತ್ತು ರ‍್ಯಾಂಪ್', 'पार्किंग क्षेत्र और रैंप', 'Parking', 'Courtyard', 0, 13.0114200, 77.5686500, TRUE, FALSE, 'Campus vehicle parking lot and accessible wheelchair ramp inside the main gate.'),
('LOC_030', 'PU College Stairs (Floor 1)', 'ಪಿಯು ಕಾಲೇಜು ಮೆಟ್ಟಿಲುಗಳು (ಮೊದಲ ಮಹಡಿ)', 'पीयू कॉलेज सीढ़ियाँ (प्रथम तल)', 'Transit', 'North Wing', 1, 13.0115500, 77.5686000, FALSE, FALSE, 'First floor landing of the north-west staircase next to Biotechnology labs and Classroom F4.'),
('LOC_031', 'South Staircase (Floor 1)', 'ದಕ್ಷಿಣ ಮೆಟ್ಟಿಲುಗಳು (ಮೊದಲ ಮಹಡಿ)', 'दक्षिणी सीढ़ियाँ (प्रथम तल)', 'Transit', 'South Wing', 1, 13.0118500, 77.5686800, FALSE, FALSE, 'First floor landing of the south staircase next to Physics labs and Student Washroom.'),
('LOC_032', 'Campus Central Elevator (Floor 1)', 'ಕಾಲೇಜು ಕೇಂದ್ರೀಯ ಲಿಫ್ಟ್ (ಮೊದಲ ಮಹಡಿ)', 'कॉलेज केंद्रीय लिफ्ट (प्रथम तल)', 'Transit', 'North Wing', 1, 13.0115500, 77.5686200, TRUE, TRUE, 'First-floor landing of the accessible central elevator by the north corridor.'),
('LOC_033', 'Biotechnology Lab (PG)', 'ಬಯೋಟೆಕ್ನಾಲಜಿ ಲ್ಯಾಬ್ (ಪಿಜಿ)', 'बायोटेक्नोलॉजी लैब (पीजी)', 'Lab', 'North Wing', 1, 13.0115700, 77.5686100, TRUE, TRUE, 'Postgraduate biotechnology laboratory at the north corridor apex.'),
('LOC_034', 'Biotechnology Lab (UG)', 'ಬಯೋಟೆಕ್ನಾಲಜಿ ಲ್ಯಾಬ್ (ಯುಜಿ)', 'बायोटेक्नोलॉजी लैब (यूजी)', 'Lab', 'North Wing', 1, 13.0115800, 77.5686300, TRUE, TRUE, 'Undergraduate biotechnology laboratory directly adjacent to PG Biotech Lab.'),
('LOC_035', 'Faculty Washroom (First Floor)', 'ಅಧ್ಯಾಪಕರ ಶೌಚಾಲಯ (ಮೊದಲ ಮಹಡಿ)', 'शिक्षक शौचालय (प्रथम तल)', 'Facility', 'North Wing', 1, 13.0115400, 77.5686300, TRUE, TRUE, 'Staff and faculty restroom on the north corridor near PU stairs.'),
('LOC_036', 'Classroom F4', 'ತರಗತಿ ಕೊಠಡಿ ಎಫ್ ೪', 'कक्षा एफ 4', 'Classroom', 'North Wing', 1, 13.0115300, 77.5686600, TRUE, TRUE, 'First floor lecture classroom facing the parking lot view.'),
('LOC_037', 'Classroom F3', 'ತರಗತಿ ಕೊಠಡಿ ಎಫ್ ೩', 'कक्षा एफ 3', 'Classroom', 'North Wing', 1, 13.0115200, 77.5686900, TRUE, TRUE, 'First floor lecture classroom directly adjacent to Classroom F4.'),
('LOC_038', 'Classroom F2', 'ತರಗತಿ ಕೊಠಡಿ ಎಫ್ ೨', 'कक्षा एफ 2', 'Classroom', 'North Wing', 1, 13.0115100, 77.5687200, TRUE, TRUE, 'First floor lecture classroom directly adjacent to Classroom F3 and Dept. of Botany.'),
('LOC_039', 'Dept. of Botany', 'ಸಸ್ಯಶಾಸ್ತ್ರ ವಿಭಾಗ', 'वनस्पति विज्ञान विभाग', 'Academic', 'North Wing', 1, 13.0115000, 77.5687400, TRUE, TRUE, 'Department of Botany faculty chamber located right between Classroom F2 and Dept. of Journalism.'),
('LOC_040', 'Classroom F1', 'ತರಗತಿ ಕೊಠಡಿ ಎಫ್ ೧', 'कक्षा एफ 1', 'Classroom', 'North Wing', 1, 13.0114900, 77.5687100, TRUE, TRUE, 'First floor classroom situated in the inner corridor adjacent to F2 and Botany.'),
('LOC_041', 'Dept. of Journalism', 'ಪತ್ರಿಕೋದ್ಯಮ ವಿಭಾಗ', 'पत्रकारिता विभाग', 'Academic', 'West Wing', 1, 13.0114900, 77.5687700, TRUE, TRUE, 'Department of Journalism faculty chamber on the corner hallway.'),
('LOC_042', 'Botany Lab (PG)', 'ಬಾಟನಿ ಲ್ಯಾಬ್ (ಪಿಜಿ)', 'वनस्पति विज्ञान लैब (पीजी)', 'Lab', 'West Wing', 1, 13.0115000, 77.5687900, TRUE, TRUE, 'Postgraduate botany laboratory located on the left side of Journalism department.'),
('LOC_043', 'Botany Lab (UG)', 'ಬಾಟನಿ ಲ್ಯಾಬ್ (ಯುಜಿ)', 'वनस्पति विज्ञान लैब (यूजी)', 'Lab', 'West Wing', 1, 13.0115200, 77.5688100, TRUE, TRUE, 'Undergraduate botany laboratory adjacent to Botany PG Lab.'),
('LOC_044', 'Microbiology Lab (Floor 1)', 'ಮೈಕ್ರೋಬಯಾಲಜಿ ಲ್ಯಾಬ್ (ಮೊದಲ ಮಹಡಿ)', 'माइक्रोबायोलॉजी लैब (प्रथम तल)', 'Lab', 'West Wing', 1, 13.0115500, 77.5688200, TRUE, TRUE, 'First floor microbiology laboratory along the west corridor leading towards Classroom F5.'),
('LOC_045', 'Classroom F5', 'ತರಗತಿ ಕೊಠಡಿ ಎಫ್ ೫', 'कक्षा एफ 5', 'Classroom', 'West Wing', 1, 13.0116000, 77.5688300, TRUE, TRUE, 'Prominent corner classroom on the first floor at the junction of the west and south wings.'),
('LOC_046', 'Physics Lab III', 'ಭೌತಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೩', 'भौतिक विज्ञान प्रयोगशाला 3', 'Lab', 'South Wing', 1, 13.0116300, 77.5688200, TRUE, TRUE, 'Physics research and practical laboratory located right next to Classroom F5 down a short hallway cut.'),
('LOC_047', 'Dept. of Physics (UG) & Faculty Chamber', 'ಭೌತಶಾಸ್ತ್ರ ವಿಭಾಗ (ಯುಜಿ)', 'भौतिक विज्ञान विभाग (यूजी)', 'Academic', 'South Wing', 1, 13.0116600, 77.5688000, TRUE, TRUE, 'Undergraduate physics department and faculty consultation chamber.'),
('LOC_048', 'Physics Lab II', 'ಭೌತಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೨', 'भौतिक विज्ञान प्रयोगशाला 2', 'Lab', 'South Wing', 1, 13.0116900, 77.5687800, TRUE, TRUE, 'Core physics laboratory along the south hallway with prominent overhead bilingual nameplate.'),
('LOC_049', 'Dept. of Physics (PU)', 'ಭೌತಶಾಸ್ತ್ರ ವಿಭಾಗ (ಪಿಯು)', 'भौतिक विज्ञान विभाग (पीयू)', 'Academic', 'South Wing', 1, 13.0117200, 77.5687600, TRUE, TRUE, 'PU physics faculty room and academic section.'),
('LOC_050', 'Physics Lab I', 'ಭೌತಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೧', 'भौतिक विज्ञान प्रयोगशाला 1', 'Lab', 'South Wing', 1, 13.0117500, 77.5687400, TRUE, TRUE, 'General physics practical laboratory next to South Staircase.'),
('LOC_051', 'Floor 1 Student Washroom', 'ವಿದ್ಯಾರ್ಥಿನಿಯರ ಶೌಚಾಲಯ (ಮೊದಲ ಮಹಡಿ)', 'छात्राओं का शौचालय (प्रथम तल)', 'Facility', 'South Wing', 1, 13.0117900, 77.5687200, TRUE, TRUE, 'Spacious first-floor student washroom at the end of the south corridor.'),
('LOC_052', 'Dept. of Chemistry & Staff Room', 'ರಸಾಯನಶಾಸ್ತ್ರ ವಿಭಾಗ ಮತ್ತು ಸಿಬ್ಬಂದಿ ಕೊಠಡಿ', 'रसायन विज्ञान विभाग और स्टाफ रूम', 'Academic', 'East Wing', 1, 13.0117800, 77.5686900, TRUE, TRUE, 'Chemistry faculty department and staff room next to student washrooms.'),
('LOC_053', 'Chemistry Lab I', 'ರಸಾಯನಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೧', 'रसायन विज्ञान प्रयोगशाला 1', 'Lab', 'East Wing', 1, 13.0117500, 77.5686700, TRUE, TRUE, 'First floor chemistry practical laboratory.'),
('LOC_054', 'Chemistry Research Centre', 'ರಸಾಯನಶಾಸ್ತ್ರ ಸಂಶೋಧನಾ ಕೇಂದ್ರ', 'रसायन विज्ञान अनुसंधान केंद्र', 'Lab', 'East Wing', 1, 13.0117200, 77.5686600, TRUE, TRUE, 'Advanced chemistry analytical research centre.'),
('LOC_055', 'Chemistry Lab II', 'ರಸಾಯನಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೨', 'रसायन विज्ञान प्रयोगशाला 2', 'Lab', 'East Wing', 1, 13.0116900, 77.5686500, TRUE, TRUE, 'Organic and physical chemistry laboratory along east corridor.'),
('LOC_056', 'Chemistry Lab III', 'ರಸಾಯನಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ ೩', 'रसायन विज्ञान प्रयोगशाला 3', 'Lab', 'East Wing', 1, 13.0116600, 77.5686400, TRUE, TRUE, 'Advanced chemistry lab adjacent to Biochemistry PG Lab.'),
('LOC_057', 'Biochemistry Lab (PG)', 'ಬಯೋಕೆಮಿಸ್ಟ್ರಿ ಲ್ಯಾಬ್ (ಪಿಜಿ)', 'बायोकेमिस्ट्री लैब (पीजी)', 'Lab', 'East Wing', 1, 13.0116300, 77.5686300, TRUE, TRUE, 'Postgraduate biochemistry laboratory along the east hallway.'),
('LOC_058', 'Dept. of Life Sciences Staff Room', 'ಜೀವವಿಜ್ಞಾನ ವಿಭಾಗದ ಅಧ್ಯಾಪಕರ ಕೊಠಡಿ', 'जीवन विज्ञान संकाय कक्ष', 'Academic', 'East Wing', 1, 13.0116100, 77.5686300, TRUE, TRUE, 'Joint staff room for Zoology, Biotechnology, and Biochemistry faculty.'),
('LOC_059', 'Zoology Lab (UG)', 'ಪ್ರಾಣಿಶಾಸ್ತ್ರ ಪ್ರಯೋಗಾಲಯ (ಯುಜಿ)', 'प्राणी विज्ञान प्रयोगशाला (यूजी)', 'Lab', 'East Wing', 1, 13.0115900, 77.5686300, TRUE, TRUE, 'Undergraduate zoology practical laboratory closing the quadrangle ring towards Biotech UG Lab.'),
('LOC_060', 'PU College Stairs (Floor 2)', 'ಪಿಯು ಕಾಲೇಜು ಮೆಟ್ಟಿಲುಗಳು (ಎರಡನೇ ಮಹಡಿ)', 'पीयू कॉलेज सीढ़ियाँ (द्वितीय तल)', 'Transit', 'West Wing', 2, 13.0115500, 77.5686000, FALSE, FALSE, 'Second floor landing of the north-west PU College staircase connecting West Wing classrooms S1-S3.'),
('LOC_061', 'Campus Central Elevator (Floor 2)', 'ಕಾಲೇಜು ಕೇಂದ್ರೀಯ ಲಿಫ್ಟ್ (ಎರಡನೇ ಮಹಡಿ)', 'कॉलेज केंद्रीय लिफ्ट (द्वितीय तल)', 'Transit', 'West Wing', 2, 13.0115500, 77.5686200, TRUE, TRUE, 'Second floor landing of the accessible central elevator next to Central Library and Classroom S3.'),
('LOC_062', 'Classroom S1', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೧', 'कक्षा एस 1', 'Classroom', 'West Wing', 2, 13.0115800, 77.5686000, TRUE, TRUE, 'Second floor lecture classroom located near PU College Stairs and connector corridor leading to S9-S12.'),
('LOC_063', 'Classroom S2', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೨', 'कक्षा एस 2', 'Classroom', 'West Wing', 2, 13.0116100, 77.5686000, TRUE, TRUE, 'Second floor lecture classroom situated between Classroom S1 and Classroom S3.'),
('LOC_064', 'Classroom S3', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೩', 'कक्षा एस 3', 'Classroom', 'West Wing', 2, 13.0116400, 77.5686000, TRUE, TRUE, 'Second floor lecture classroom right beside the central elevator and restroom block.'),
('LOC_065', 'Floor 2 West Restroom', 'ಶೌಚಾಲಯ (ಎರಡನೇ ಮಹಡಿ ಪಶ್ಚಿಮ)', 'शौचालय (द्वितीय तल पश्चिम)', 'Facility', 'West Wing', 2, 13.0116500, 77.5686100, TRUE, TRUE, 'Restrooms on the second floor West Wing adjacent to Central Elevator and Classroom S3.'),
('LOC_066', 'Central Library', 'ಕೇಂದ್ರ ಗ್ರಂಥಾಲಯ', 'केंद्रीय पुस्तकालय', 'Library', 'Library Wing', 0, 13.0116800, 77.5687200, TRUE, TRUE, 'Main central college library on the ground floor with wide double entrance doors and book circulation counters, directly accessible from the courtyard.'),
('LOC_067', 'Mathematics Department', 'ಗಣಿತಶಾಸ್ತ್ರ ವಿಭಾಗ', 'गणित विभाग', 'Academic', 'West Wing', 2, 13.0116900, 77.5686500, TRUE, TRUE, 'Department of Mathematics faculty chambers adjacent to Central Library.'),
('LOC_068', 'Classroom S4', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೪', 'कक्षा एस 4', 'Classroom', 'West Wing', 2, 13.0117200, 77.5686400, TRUE, TRUE, 'Second floor lecture classroom past Central Library along the upper west corridor.'),
('LOC_069', 'Classroom S5', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೫', 'कक्षा एस 5', 'Classroom', 'West Wing', 2, 13.0117500, 77.5686500, TRUE, TRUE, 'Second floor classroom near the north apex restroom and corridor crossover.'),
('LOC_070', 'Floor 2 North Apex Restroom', 'ಉತ್ತರ ಶೌಚಾಲಯ (ಎರಡನೇ ಮಹಡಿ)', 'उत्तर शौचालय (द्वितीय तल)', 'Facility', 'West Wing', 2, 13.0117800, 77.5686600, TRUE, TRUE, 'Second floor staff and student washrooms at the northern apex of the college building.'),
('LOC_071', 'North-East Staircase (Floor 2)', 'ಈಶಾನ್ಯ ಮೆಟ್ಟಿಲುಗಳು (ಎರಡನೇ ಮಹಡಿ)', 'उत्तर-पूर्वी सीढ़ियाँ (द्वितीय तल)', 'Transit', 'East Wing', 2, 13.0118000, 77.5686800, FALSE, FALSE, 'Second floor landing of the north-east staircase leading to Classroom S6 and computer labs.'),
('LOC_072', 'Classroom S6', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೬', 'कक्षा एस 6', 'Classroom', 'East Wing', 2, 13.0117800, 77.5687000, TRUE, TRUE, 'Second floor classroom at the northern head of the East Wing corridor near North-East stairs.'),
('LOC_073', 'Classroom S7', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೭', 'कक्षा एस 7', 'Classroom', 'East Wing', 2, 13.0117500, 77.5687100, TRUE, TRUE, 'Second floor classroom adjacent to Classroom S6 and Computer Lab 1.'),
('LOC_074', 'Computer Lab 1', 'ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೧', 'कंप्यूटर लैब 1', 'Lab', 'East Wing', 2, 13.0117200, 77.5687200, TRUE, TRUE, 'Main air-conditioned high-performance computer science and programming laboratory.'),
('LOC_075', 'Dept. of Computer Science & Staff Room', 'ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್ ವಿಭಾಗ ಮತ್ತು ಸಿಬ್ಬಂದಿ ಕೊಠಡಿ', 'कंप्यूटर विज्ञान विभाग और स्टाफ रूम', 'Academic', 'East Wing', 2, 13.0116900, 77.5687300, TRUE, TRUE, 'Department of Computer Science faculty consultation chambers, conference room, and staff room.'),
('LOC_076', 'Classroom S8', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೮', 'कक्षा एस 8', 'Classroom', 'East Wing', 2, 13.0116600, 77.5687400, TRUE, TRUE, 'Second floor lecture classroom situated between Computer Lab 1 and Computer Lab 2.'),
('LOC_077', 'Computer Lab 2', 'ಕಂಪ್ಯೂಟರ್ ಲ್ಯಾಬ್ ೨', 'कंप्यूटर लैब 2', 'Lab', 'East Wing', 2, 13.0116300, 77.5687500, TRUE, TRUE, 'Second floor computer lab for software development, database systems, and data science practicals.'),
('LOC_078', 'Electronics & Hardware Lab', 'ಎಲೆಕ್ಟ್ರಾನಿಕ್ಸ್ ಮತ್ತು ಹಾರ್ಡ್‌ವೇರ್ ಲ್ಯಾಬ್', 'इलेक्ट्रॉनिक्स और हार्डवेयर लैब', 'Lab', 'East Wing', 2, 13.0116000, 77.5687600, TRUE, TRUE, 'Electronics circuits, microprocessors, and hardware experimentation laboratory.'),
('LOC_079', 'Language Lab', 'ಭಾಷಾ ಪ್ರಯೋಗಾಲಯ', 'भाषा प्रयोगशाला', 'Lab', 'East Wing', 2, 13.0115700, 77.5687600, TRUE, TRUE, 'Digital language and communication skills laboratory equipped with multimedia workstations.'),
('LOC_080', 'Dept. of Commerce & Management (BBA)', 'ವಾಣಿಜ್ಯ ಮತ್ತು ನಿರ್ವಹಣಾ ವಿಭಾಗ (ಬಿಬಿಎ)', 'वाणिज्य एवं प्रबंधन विभाग (बीबीए)', 'Academic', 'East Wing', 2, 13.0115400, 77.5687700, TRUE, TRUE, 'Faculty chambers for Commerce (B.Com) and Management Studies (BBA) departments.'),
('LOC_081', 'KNV Shastri Auditorium', 'ಕೆಎನ್‌ವಿ ಶಾಸ್ತ್ರಿ ಸಭಾಂಗಣ', 'केएनवी शास्त्री ऑडिटोरियम', 'Hall', 'East Wing', 2, 13.0115100, 77.5687800, TRUE, TRUE, 'KNV Shastri Auditorium and stage hall on the second floor.'),
('LOC_082', 'South Staircase (Floor 2)', 'ದಕ್ಷಿಣ ಮೆಟ್ಟಿಲುಗಳು (ಎರಡನೇ ಮಹಡಿ)', 'दक्षिणी सीढ़ियाँ (द्वितीय तल)', 'Transit', 'South Wing', 2, 13.0118500, 77.5686800, FALSE, FALSE, 'Second floor landing of the south staircase near Commerce faculty chambers and KNV Shastri Auditorium.'),
('LOC_083', 'Classroom S9', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೯', 'कक्षा एस 9', 'Classroom', 'Connector Corridor', 2, 13.0115300, 77.5686400, TRUE, TRUE, 'Newly added second floor classroom located at the western entrance of the connector corridor near Classroom S1.'),
('LOC_084', 'Classroom S10', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೧೦', 'कक्षा एस 10', 'Classroom', 'Connector Corridor', 2, 13.0115200, 77.5686700, TRUE, TRUE, 'Newly added modern lecture classroom along the second-floor south connector corridor.'),
('LOC_085', 'Classroom S11', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೧೧', 'कक्षा एस 11', 'Classroom', 'Connector Corridor', 2, 13.0115000, 77.5687000, TRUE, TRUE, 'Newly added modern lecture classroom featuring polished wooden striped flooring along the connector corridor.'),
('LOC_086', 'Classroom S12', 'ತರಗತಿ ಕೊಠಡಿ ಎಸ್ ೧೨', 'कक्षा एस 12', 'Classroom', 'Connector Corridor', 2, 13.0114800, 77.5687300, TRUE, TRUE, 'Newly added second floor classroom positioned right at the corridor end by the scenic glazed angled window and Main Reception Staircase.'),
('LOC_087', 'Main Reception Staircase (Floor 2)', 'ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲು (ಎರಡನೇ ಮಹಡಿ)', 'मुख्य स्वागत सीढ़ियाँ (द्वितीय तल)', 'Transit', 'Admin Block', 2, 13.0114600, 77.5687350, FALSE, FALSE, 'Second floor landing of the central main reception staircase, opening right in front of Classroom S12 and connector corridor.'),
('LOC_088', 'PU College Stairs (Floor 3)', 'ಪಿಯು ಕಾಲೇಜು ಮೆಟ್ಟಿಲುಗಳು (ಮೂರನೇ ಮಹಡಿ)', 'पीयू कॉलेज सीढ़ियाँ (तृतीय तल)', 'Transit', 'West Wing', 3, 13.0115500, 77.5686000, FALSE, FALSE, 'Third floor landing of the north-west staircase adjacent to Tissue Culture Lab and Biotech Research.'),
('LOC_089', 'Campus Central Elevator (Floor 3)', 'ಕಾಲೇಜು ಕೇಂದ್ರೀಯ ಲಿಫ್ಟ್ (ಮೂರನೇ ಮಹಡಿ)', 'कॉलेज केंद्रीय लिफ्ट (तृतीय तल)', 'Transit', 'West Wing', 3, 13.0115500, 77.5686200, TRUE, TRUE, 'Third floor landing of the accessible central elevator serving the research laboratories and third-floor Student Lounge.'),
('LOC_090', 'Animal Cell Culture Lab', 'ಪ್ರಾಣಿಕೋಶ ಕೃಷಿ ಪ್ರಯೋಗಾಲಯ', 'पशु कोशिका संवर्धन प्रयोगशाला', 'Lab', 'PG Science Wing', 3, 13.0115800, 77.5686100, TRUE, TRUE, 'Advanced cell culture and sterile in-vitro biotechnology research laboratory on the 3rd floor west wing.'),
('LOC_091', 'Biotechnology Research Lab', 'ಬಯೋಟೆಕ್ನಾಲಜಿ ಸಂಶೋಧನಾ ಪ್ರಯೋಗಾಲಯ', 'बायोटेक्नोलॉजी अनुसंधान प्रयोगशाला', 'Lab', 'PG Science Wing', 3, 13.0116100, 77.5686200, TRUE, TRUE, 'Advanced molecular biotechnology and genetic engineering research laboratory on the 3rd floor west wing.'),
('LOC_092', 'Classroom PG T1', 'ತರಗತಿ ಕೊಠಡಿ ಪಿಜಿ ಟಿ ೧', 'कक्षा पीजी टी 1', 'Classroom', 'PG Block', 3, 13.0116400, 77.5686300, TRUE, TRUE, 'Postgraduate lecture classroom PG T1 on the third floor corridor.'),
('LOC_093', 'Library (PG)', 'ಗ್ರಂಥಾಲಯ (ಸ್ನಾತಕೋತ್ತರ)', 'पुस्तकालय (पीजी)', 'Library', 'PG Block', 3, 13.0116600, 77.5686400, TRUE, TRUE, 'Dedicated departmental postgraduate reference library with extensive academic research collections.'),
('LOC_094', 'Main Reception Staircase (Floor 3)', 'ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲು (ಮೂರನೇ ಮಹಡಿ)', 'मुख्य स्वागत सीढ़ियाँ (तृतीय तल)', 'Transit', 'Admin Block', 3, 13.0114600, 77.5687350, FALSE, FALSE, 'Third floor summit landing of the main reception staircase opening directly onto the Student Open Lounge.'),
('LOC_095', 'Student Open Lounge (Third Floor Level)', 'ವಿದ್ಯಾರ್ಥಿನಿಯರ ವಿಶ್ರಾಂತಿ ಲೌಂಜ್ (ಮೂರನೇ ಮಹಡಿ)', 'छात्रा ओपन लाउंज (तृतीय तल)', 'Facility', 'Courtyard Center', 3, 13.0114900, 77.5687100, TRUE, TRUE, 'Spacious elevated open student lounge with wooden striped flooring, black railings, comfortable seating, overlooking the courtyard and stairs.'),
('LOC_096', 'North-East Staircase (Floor 3)', 'ಈಶಾನ್ಯ ಮೆಟ್ಟಿಲುಗಳು (ಮೂರನೇ ಮಹಡಿ)', 'उत्तर-पूर्वी सीढ़ियाँ (तृतीय तल)', 'Transit', 'East Wing', 3, 13.0118000, 77.5686800, FALSE, FALSE, 'Third floor landing of the north-east staircase leading to Third Floor Lecture Hall.'),
('LOC_097', 'Third Floor Lecture Hall', 'ಉಪನ್ಯಾಸ ಭವನ (ಮೂರನೇ ಮಹಡಿ)', 'व्याख्यान हॉल (तृतीय तल)', 'Classroom', 'East Wing', 3, 13.0117600, 77.5687100, TRUE, TRUE, 'Large tiered lecture hall equipped with audiovisual projection for inter-departmental lectures and seminars.'),
('LOC_098', 'Business Lab', 'ವಾಣಿಜ್ಯ ಪ್ರಯೋಗಾಲಯ', 'बिजनेस लैब', 'Lab', 'PG Commerce Wing', 3, 13.0117200, 77.5687300, TRUE, TRUE, 'Specialized business simulations and commerce analytics laboratory on the 3rd floor.'),
('LOC_099', 'Dept. of Commerce (UG & PG)', 'ವಾಣಿಜ್ಯ ವಿಭಾಗ (ಯುಜಿ ಮತ್ತು ಪಿಜಿ)', 'वाणिज्य विभाग (यूजी और पीजी)', 'Academic', 'PG Commerce Wing', 3, 13.0116800, 77.5687500, TRUE, TRUE, 'Department of Commerce faculty chambers and administrative wing on the 3rd floor.'),
('LOC_100', 'Dept. of Commerce Research Centre & UGC Centre', 'ವಾಣಿಜ್ಯ ಸಂಶೋಧನಾ ಕೇಂದ್ರ ಮತ್ತು ಯುಜಿಸಿ ಕೇಂದ್ರ', 'वाणिज्य अनुसंधान केंद्र और यूजीसी नेटवर्क केंद्र', 'Research', 'PG Commerce Wing', 3, 13.0116300, 77.5687700, TRUE, TRUE, 'Commerce Ph.D. research centre and UGC network computer research facility.'),
('LOC_101', 'DBT-Bioinformatics Facility', 'ಡಿಬಿಟಿ ಬಯೋಇನ್ಫಾರ್ಮ್ಯಾಟಿಕ್ಸ್ ಪ್ರಯೋಗಾಲಯ', 'डीबीटी बायोइन्फॉर्मेटिक्स प्रयोगशाला', 'Lab', 'PG Science Wing', 3, 13.0115800, 77.5687800, TRUE, TRUE, 'Department of Biotechnology funded bioinformatics workstation lab and computational genomics center.'),
('LOC_102', 'South Staircase (Floor 3)', 'ದಕ್ಷಿಣ ಮೆಟ್ಟಿಲುಗಳು (ಮೂರನೇ ಮಹಡಿ)', 'दक्षिणी सीढ़ियाँ (तृतीय तल)', 'Transit', 'South Wing', 3, 13.0118500, 77.5686800, FALSE, FALSE, 'Third floor landing of the south staircase near Instrumentation Room and Project Lab.'),
('LOC_103', 'Main Reception Staircase', 'ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲು (ರಿಸೆಪ್ಷನ್ ಎದುರು)', 'मुख्य स्वागत सीढ़ियाँ (रिसेप्शन के सामने)', 'Transit', 'Admin Block', 0, 13.0114600, 77.5687350, FALSE, FALSE, 'Main entrance staircase located directly opposite the reception desk and Administrative Block Foyer. Offers the quickest direct stairs access to upper floors.'),
('LOC_104', 'Main Reception Staircase (Floor 1)', 'ಮುಖ್ಯ ಸ್ವಾಗತ ಮೆಟ್ಟಿಲು (ಮೊದಲ ಮಹಡಿ)', 'मुख्य स्वागत सीढ़ियाँ (प्रथम तल)', 'Transit', 'North Wing', 1, 13.0114600, 77.5687350, FALSE, FALSE, 'First floor landing of the main reception staircase, opening directly towards Classroom F1, F4, Botany, and Biotech labs.'),
('LOC_108', 'Smritimaya mLAC Museum', 'ಸ್ಮೃತಿಮಯ mLAC ಮ್ಯೂಸಿಯಂ', 'स्मृतिमय mLAC संग्रहालय', 'Facility', 'Library Wing', 0, 13.0116600, 77.5687300, TRUE, FALSE, 'College heritage archive museum showcasing institution history, founder memorials, and cultural artifacts, beside Central Library.'),
('LOC_109', 'Fee Counters', 'ಶುಲ್ಕ ಪಾವತಿ ಸ್ಥಳ', 'शुल्क भुगतान काउंटर', 'Administration', 'Admin Block', 0, 13.0116400, 77.5687000, TRUE, FALSE, 'Student fee collection counters 1, 2, and 3 located on the ground floor with sheltered queue canopy.'),
('LOC_110', 'Health Centre', 'ಆರೋಗ್ಯ ಕೇಂದ್ರ', 'स्वास्थ्य केंद्र', 'Medical', 'Rear Service Wing', 0, 13.0112800, 77.5688500, TRUE, FALSE, 'College medical health centre and first aid infirmary along the paved canteen service pathway.'),
('LOC_111', 'Gents Washroom', 'ಪುರುಷರ ಶೌಚಾಲಯ', 'पुरुष शौचालय', 'Restroom', 'Rear Service Wing', 0, 13.0112400, 77.5688700, TRUE, FALSE, 'Ground floor gentlemen washroom located past the health center along the garden perimeter corridor.'),
('LOC_112', 'mLAC Garden', 'ಎಂಎಲ್‌ಎಸಿ ಉದ್ಯಾನವನ', 'mLAC उद्यान', 'Outdoor', 'Campus Grounds', 0, 13.0112000, 77.5689000, TRUE, FALSE, 'Lush botanical green garden with paved walking paths, benches, flowering plants, and medicinal flora.'),
('LOC_113', 'Dept. of Psychology', 'ಮನೋವಿಜ್ಞಾನ ವಿಭಾಗ', 'मनोविज्ञान विभाग', 'Academic', 'South Lecture Wing', 0, 13.0113200, 77.5688200, TRUE, FALSE, 'Department of Psychology faculty chamber and student counseling center directly beside Classroom G9.'),
('LOC_114', 'Dept. of English, Hindi & Sanskrit', 'ಆಂಗ್ಲ, ಹಿಂದಿ ಮತ್ತು ಸಂಸ್ಕೃತ ವಿಭಾಗ', 'अंग्रेजी, हिंदी एवं संस्कृत विभाग', 'Academic', 'South Lecture Wing', 0, 13.0112500, 77.5688400, TRUE, FALSE, 'Languages faculty staff room for English, Hindi, and Sanskrit departments at the end of Classroom G11 corridor.'),
('LOC_115', 'Classroom PG T2 & T3', 'ತರಗತಿ ಕೊಠಡಿ ಪಿಜಿ ಟಿ ೨ ಮತ್ತು ಟಿ ೩', 'कक्षा पीजी टी 2 और टी 3', 'Classroom', 'PG Block', 3, 13.0116000, 77.5686500, TRUE, TRUE, 'Postgraduate lecture classrooms PG T2 and PG T3 situated adjacent to PG Library.'),
('LOC_116', 'Classroom PG T5 & T6', 'ತರಗತಿ ಕೊಠಡಿ ಪಿಜಿ ಟಿ ೫ ಮತ್ತು ಟಿ ೬', 'कक्षा पीजी टी 5 और टी 6', 'Classroom', 'PG Block', 3, 13.0117400, 77.5687300, TRUE, TRUE, 'Postgraduate tutorial rooms PG T5 and PG T6 leading toward the NCC store.'),
('LOC_117', 'mLAC - KSCST - IP Cell (PG T7)', 'ಐಪಿ ಸೆಲ್ ಮತ್ತು ತರಗತಿ ಪಿಜಿ ಟಿ ೭', 'आईपी सेल और कक्षा पीजी टी 7', 'Academic', 'PG Block', 3, 13.0117200, 77.5687200, TRUE, TRUE, 'Intellectual Property rights cell and PG tutorial classroom PG T7.'),
('LOC_118', 'Classroom PG T8', 'ತರಗತಿ ಕೊಠಡಿ ಪಿಜಿ ಟಿ ೮', 'कक्षा पीजी टी 8', 'Classroom', 'PG Block', 3, 13.0117000, 77.5687000, TRUE, TRUE, 'Postgraduate classroom PG T8 directly facing the 3rd floor landing mirror.'),
('LOC_119', '1 KAR Air SQN NCC & NCC Store', '೧ ಕರ್ ಏರ್ ಸ್ಕ್ವಾಡ್ರನ್ ಎನ್‌ಸಿಸಿ ಮತ್ತು ದಾಸ್ತಾನು', '1 कर एयर स्क्वाड्रन एनसीसी और एनसीसी स्टोर', 'Facility', 'Third Floor Terrace Wing', 3, 13.0117700, 77.5687500, TRUE, TRUE, 'National Cadet Corps (NCC) Air Wing headquarters, uniform store, and cadet training office on the 3rd floor.'),
('LOC_120', 'Girls Wash Room (Student Lounge)', 'ವಿದ್ಯಾರ್ಥಿನಿಯರ ಶೌಚಾಲಯ (ಲೌಂಜ್)', 'गर्ल्स वॉश रूम (लाउंज)', 'Restroom', 'Third Floor Level', 3, 13.0115000, 77.5687300, TRUE, TRUE, 'Dedicated clean restroom facility inside the Student Open Lounge hall.'),
('LOC_121', 'Green Room (Student Lounge)', 'ಗ್ರೀನ್ ರೂಮ್ (ಲೌಂಜ್)', 'ग्रीन रूम (लाउंज)', 'Facility', 'Third Floor Level', 3, 13.0115100, 77.5687350, TRUE, TRUE, 'Costume changing and backstage rehearsal green room inside the Student Open Lounge hall.'),
('LOC_122', 'Life Science Research Centre', 'ಜೀವವಿಜ್ಞಾನ ಸಂಶೋಧನಾ ಕೇಂದ್ರ', 'लाइफ साइंस रिसर्च सेंटर', 'Lab', 'PG Science Wing', 3, 13.0116000, 77.5686150, TRUE, TRUE, 'Interdisciplinary life sciences research centre beside Animal Cell Culture Lab and Biotechnology Research Lab.');

-- 12. Departments Seeds
INSERT INTO departments (department_id, department_name, kannada_name, hindi_name, block, floor, location_id, hod_name, contact_email, phone_ext) VALUES
('DEPT_01', 'Computer Science', 'ಕಂಪ್ಯೂಟರ್ ಸೈನ್ಸ್', 'कंप्यूटर साइंस', 'East Wing', 2, 'LOC_075', 'Dr. S. V. Manjula', 'cs.hod@mlacw.edu.in', '2101'),
('DEPT_02', 'Information Science', 'ಮಾಹಿತಿ ವಿಜ್ಞಾನ', 'सूचना विज्ञान', 'East Wing', 2, 'LOC_077', 'Prof. R. Geetha', 'is.dept@mlacw.edu.in', '2102'),
('DEPT_03', 'Mathematics', 'ಗಣಿತಶಾಸ್ತ್ರ', 'गणित', 'West Wing', 2, 'LOC_067', 'Dr. N. Gayathri', 'maths.hod@mlacw.edu.in', '2103'),
('DEPT_04', 'Physics', 'ಭೌತಶಾಸ್ತ್ರ', 'भौतिकी', 'South Wing', 1, 'LOC_047', 'Dr. B. K. Sharada', 'physics.dept@mlacw.edu.in', '2201'),
('DEPT_05', 'Chemistry', 'ರಸಾಯನಶಾಸ್ತ್ರ', 'रसायन विज्ञान', 'East Wing', 1, 'LOC_052', 'Dr. P. Pushpalatha', 'chem.dept@mlacw.edu.in', '2202'),
('DEPT_06', 'Biotechnology', 'ಜೈವಿಕ ತಂತ್ರಜ್ಞಾನ', 'बायोटेक्नोलॉजी', 'West Wing', 3, 'LOC_091', 'Dr. K. S. Anuradha', 'biotech.dept@mlacw.edu.in', '2301'),
('DEPT_07', 'Microbiology', 'ಸೂಕ್ಷ್ಮಜೀವವಿಜ್ಞಾನ', 'माइक्रोबायोलॉजी', 'West Wing', 3, 'LOC_092', 'Dr. S. Bhavani', 'microbio.dept@mlacw.edu.in', '2302'),
('DEPT_08', 'Commerce', 'ವಾಣಿಜ್ಯ', 'वाणिज्य', 'PG Commerce Wing', 3, 'LOC_099', 'Dr. M. Lalitha', 'commerce.hod@mlacw.edu.in', '2401'),
('DEPT_09', 'Management (BBA)', 'ವ್ಯವಹಾರ ನಿರ್ವಹಣೆ', 'प्रबंधन', 'East Wing', 2, 'LOC_080', 'Prof. Deepa Kamath', 'bba.hod@mlacw.edu.in', '2402'),
('DEPT_10', 'English', 'ಇಂಗ್ಲಿಷ್', 'अंग्रेजी', 'South Lecture Wing', 0, 'LOC_114', 'Dr. Anitha Rao', 'english.dept@mlacw.edu.in', '2501'),
('DEPT_11', 'Kannada', 'ಕನ್ನಡ', 'कन्नड़', 'West Wing', 2, 'LOC_066', 'Dr. T. S. Ramesh', 'kannada.dept@mlacw.edu.in', '2502'),
('DEPT_12', 'Sanskrit', 'ಸಂಸ್ಕೃತ', 'संस्कृत', 'South Lecture Wing', 0, 'LOC_114', 'Dr. Vidwan Vidyashankar', 'sanskrit.dept@mlacw.edu.in', '2503'),
('DEPT_13', 'Psychology', 'ಮನಃಶಾಸ್ತ್ರ', 'मनोविज्ञान', 'South Lecture Wing', 0, 'LOC_113', 'Dr. Preethi Shenoy', 'psychology.dept@mlacw.edu.in', '2601'),
('DEPT_14', 'Journalism', 'ಪತ್ರಿಕೋದ್ಯಮ', 'पत्रकारिता', 'West Wing', 1, 'LOC_041', 'Prof. V. Sandhya', 'journalism.dept@mlacw.edu.in', '2602'),
('DEPT_15', 'Administration', 'ಆಡಳಿತ', 'प्रशासन', 'Admin Block', 0, 'LOC_003', 'Dr. Shashikala A (Principal)', 'principal@mlacw.edu.in', '2001'),
('DEPT_16', 'Botany', 'ಸಸ್ಯಶಾಸ್ತ್ರ', 'वनस्पति विज्ञान', 'North Wing', 1, 'LOC_039', 'Dr. Rekha Sethi', 'botany.dept@mlacw.edu.in', '2701'),
('DEPT_17', 'Zoology', 'ಪ್ರಾಣಿಶಾಸ್ತ್ರ', 'जंतु विज्ञान', 'East Wing', 1, 'LOC_058', 'Dr. H. S. Champa', 'zoology.dept@mlacw.edu.in', '2702'),
('DEPT_18', 'Biochemistry', 'ಬಯೋಕೆಮಿಸ್ಟ್ರಿ', 'जैव रसायन', 'East Wing', 1, 'LOC_057', 'Dr. N. Vani', 'biochem.dept@mlacw.edu.in', '2703');

-- 13. Classrooms Seeds
INSERT INTO classrooms (classroom_id, room_number, room_name, block, floor, capacity, facilities, is_wheelchair_accessible, department_id, location_id) VALUES
('CR_001', 'G1', 'Classroom G1', 'Left Wing', 0, 65, 'Smart Projector + Acoustic Audio + Podium', TRUE, 'DEPT_15', 'LOC_014'),
('CR_002', 'G2', 'Classroom G2', 'Left Wing', 0, 65, 'Smartboard + High-speed Wi-Fi', TRUE, 'DEPT_15', 'LOC_015'),
('CR_003', 'G3', 'Classroom G3', 'Left Wing', 0, 65, 'Smartboard + Ergonomic Benches', TRUE, 'DEPT_15', 'LOC_016'),
('CR_004', 'G4', 'Classroom G4', 'Left Wing', 0, 60, 'Interactive Display + Dual Speaker System', TRUE, 'DEPT_15', 'LOC_017'),
('CR_005', 'G5', 'Classroom G5', 'Left Wing', 0, 60, 'Digital Smartboard + Whiteboard', TRUE, 'DEPT_15', 'LOC_018'),
('CR_006', 'G6', 'Classroom G6', 'Left Wing', 0, 60, 'Projector + Central PA Audio', TRUE, 'DEPT_15', 'LOC_019'),
('CR_007', 'G7', 'Classroom G7', 'Left Wing', 0, 65, 'HD Screen + Faculty Mic System', TRUE, 'DEPT_15', 'LOC_020'),
('CR_008', 'G8', 'Classroom G8', 'Left Wing', 0, 65, 'Interactive Panel + Wi-Fi Hotspot', TRUE, 'DEPT_15', 'LOC_021'),
('CR_009', 'F1', 'Classroom F1', 'North Wing', 1, 65, 'Smart Projector + Acoustic Audio + Podium', TRUE, 'DEPT_15', 'LOC_040'),
('CR_010', 'F2', 'Classroom F2', 'North Wing', 1, 65, 'Smartboard + High-speed Wi-Fi', TRUE, 'DEPT_15', 'LOC_038'),
('CR_011', 'F3', 'Classroom F3', 'North Wing', 1, 65, 'Smartboard + Ergonomic Benches', TRUE, 'DEPT_15', 'LOC_037'),
('CR_012', 'F4', 'Classroom F4', 'North Wing', 1, 60, 'Interactive Display + Dual Speaker System', TRUE, 'DEPT_15', 'LOC_036'),
('CR_013', 'F5', 'Classroom F5', 'West Wing', 1, 70, 'Digital Smartboard + Whiteboard + Dual Projector', TRUE, 'DEPT_15', 'LOC_045'),
('CR_014', 'S1', 'Classroom S1', 'West Wing', 2, 65, 'Smart Projector + High-speed Wi-Fi', TRUE, 'DEPT_08', 'LOC_062'),
('CR_015', 'S2', 'Classroom S2', 'West Wing', 2, 65, 'Digital Smartboard + Whiteboard', TRUE, 'DEPT_08', 'LOC_063'),
('CR_016', 'S3', 'Classroom S3', 'West Wing', 2, 65, 'Smartboard + Audio System', TRUE, 'DEPT_08', 'LOC_064'),
('CR_017', 'S4', 'Classroom S4', 'West Wing', 2, 60, 'Interactive Flat Panel + Dual Speakers', TRUE, 'DEPT_08', 'LOC_068'),
('CR_018', 'S5', 'Classroom S5', 'West Wing', 2, 60, 'Smart Projector + Acoustic Podium', TRUE, 'DEPT_08', 'LOC_069'),
('CR_019', 'S6', 'Classroom S6', 'East Wing', 2, 65, 'Smartboard + Ergonomic Seating', TRUE, 'DEPT_01', 'LOC_072'),
('CR_020', 'S7', 'Classroom S7', 'East Wing', 2, 65, 'Interactive Panel + Digital Whiteboard', TRUE, 'DEPT_01', 'LOC_073'),
('CR_021', 'S8', 'Classroom S8', 'East Wing', 2, 60, 'Projector + Central PA Audio', TRUE, 'DEPT_01', 'LOC_076'),
('CR_022', 'S9', 'Classroom S9', 'Connector Corridor', 2, 65, 'Modern Smartboard + Wooden Striped Floor', TRUE, 'DEPT_09', 'LOC_083'),
('CR_023', 'S10', 'Classroom S10', 'Connector Corridor', 2, 65, 'Interactive Display + Acoustic Ceiling', TRUE, 'DEPT_09', 'LOC_084'),
('CR_024', 'S11', 'Classroom S11', 'Connector Corridor', 2, 65, 'Smart Projector + Polished Flooring', TRUE, 'DEPT_09', 'LOC_085'),
('CR_025', 'S12', 'Classroom S12', 'Connector Corridor', 2, 70, 'Panoramic Glazed Window + Smartboard + PA System', TRUE, 'DEPT_09', 'LOC_086'),
('CR_026', 'LH3', 'Third Floor Lecture Hall', 'East Wing', 3, 120, 'Tiered Gallery Seating + Dual HD Projection + Wireless Mic', TRUE, 'DEPT_06', 'LOC_097'),
('CR_027', 'G9', 'Classroom G9', 'Left Wing', 0, 65, 'Smart Projector + Acoustic Audio + Podium', TRUE, 'DEPT_15', 'LOC_105'),
('CR_028', 'G10', 'Classroom G10', 'Left Wing', 0, 65, 'Smartboard + High-speed Wi-Fi', TRUE, 'DEPT_15', 'LOC_106'),
('CR_029', 'G11', 'Classroom G11', 'Left Wing', 0, 65, 'Smartboard + Ergonomic Benches', TRUE, 'DEPT_15', 'LOC_107');

-- 14. Faculty Seeds
INSERT INTO faculty (faculty_id, full_name, designation, department_id, cabin_room, location_id, email, consultation_hours) VALUES
('FAC_201', 'Dr. S. V. Manjula', 'Professor & Head', 'DEPT_01', 'Dept. of Computer Science & Staff Room', 'LOC_075', 'manjula.sv@mlacw.edu.in', '10:00 AM - 12:00 PM'),
('FAC_202', 'Prof. R. Geetha', 'Associate Professor', 'DEPT_02', 'Computer Lab 2', 'LOC_077', 'geetha.r@mlacw.edu.in', '02:00 PM - 04:00 PM'),
('FAC_203', 'Dr. N. Gayathri', 'Professor', 'DEPT_03', 'Mathematics Department', 'LOC_067', 'gayathri.n@mlacw.edu.in', '11:00 AM - 01:00 PM'),
('FAC_204', 'Dr. B. K. Sharada', 'Head of Department', 'DEPT_04', 'Dept. of Physics (UG) & Faculty Chamber', 'LOC_047', 'sharada.bk@mlacw.edu.in', '09:30 AM - 11:30 AM'),
('FAC_205', 'Dr. P. Pushpalatha', 'Associate Professor', 'DEPT_05', 'Dept. of Chemistry & Staff Room', 'LOC_052', 'pushpalatha.p@mlacw.edu.in', '01:30 PM - 03:30 PM'),
('FAC_206', 'Dr. Rekha Sethi', 'Associate Professor', 'DEPT_16', 'Dept. of Botany', 'LOC_039', 'rekha.sethi@mlacw.edu.in', '10:00 AM - 12:00 PM'),
('FAC_207', 'Dr. H. S. Champa', 'Professor & Head', 'DEPT_17', 'Dept. of Life Sciences Staff Room', 'LOC_058', 'champa.hs@mlacw.edu.in', '02:00 PM - 04:00 PM'),
('FAC_208', 'Dr. Shashikala A', 'Principal', 'DEPT_15', 'Principal Office', 'LOC_004', 'principal@mlacw.edu.in', '11:00 AM - 01:00 PM');

-- 15. Students Seeds
INSERT INTO students (student_id, roll_number, full_name, department_id, program, year_of_study, section, wheelchair_user, emergency_contact) VALUES
('STU_1001', '23BCAS01', 'Ananya Sharma', 'DEPT_01', 'BCA', 2, 'A', FALSE, '+91-9845012341'),
('STU_1002', '23BCAS02', 'Bhavana Gowda', 'DEPT_01', 'BCA', 2, 'A', TRUE, '+91-9845012342'),
('STU_1003', '24BSCS01', 'Chaitra Rao', 'DEPT_01', 'B.Sc Computer Science', 1, 'B', FALSE, '+91-9845012343'),
('STU_1004', '22BCOM01', 'Divya Murthy', 'DEPT_08', 'B.Com', 3, 'A', FALSE, '+91-9845012344'),
('STU_1005', '23BBAS01', 'Farhana Taj', 'DEPT_09', 'BBA', 2, 'A', FALSE, '+91-9845012345'),
('STU_1006', '24BSCP01', 'Gowri K', 'DEPT_04', 'B.Sc Physics', 1, 'A', FALSE, '+91-9845012346'),
('STU_1007', '23BSCB01', 'Harshitha P', 'DEPT_06', 'B.Sc Biotechnology', 2, 'A', TRUE, '+91-9845012347'),
('STU_1008', '22BASK01', 'Janaki Shastri', 'DEPT_12', 'BA Sanskrit', 3, 'A', FALSE, '+91-9845012348'),
('STU_1009', '24BAPSY1', 'Keerthana Hegde', 'DEPT_13', 'BA Psychology', 1, 'A', FALSE, '+91-9845012349'),
('STU_1010', '23BAJOU1', 'Lavanya N', 'DEPT_14', 'BA Journalism', 2, 'A', FALSE, '+91-9845012350'),
('STU_1011', '24BCOM12', 'Monika S', 'DEPT_08', 'B.Com', 1, 'C', FALSE, '+91-9845012351'),
('STU_1012', '23BSCM01', 'Nandini Bhat', 'DEPT_03', 'B.Sc Mathematics', 2, 'A', FALSE, '+91-9845012352');

-- 16. Navigation Paths Seeds
INSERT INTO navigation_paths (path_id, source_node, target_node, distance_meters, path_type, is_accessible, crowd_level, transition_type) VALUES
('P_001', 'Main Gate', 'Security Cabin', 20, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_002', 'Security Cabin', 'Administrative Block Foyer', 15, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_003', 'Security Cabin', 'Main Reception Staircase', 12, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_004', 'Administrative Block Foyer', 'Main Reception Staircase', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_005', 'Campus Central Elevator', 'Main Reception Staircase', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_006', 'College Garden Walkway', 'Main Reception Staircase', 10, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_007', 'Security Cabin', 'Parking Area & Ramp', 15, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_008', 'Administrative Block Foyer', 'Principal Office', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_009', 'Administrative Block Foyer', 'Vice Principal Office', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_010', 'Administrative Block Foyer', 'Administrative Office', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_011', 'Administrative Block Foyer', 'Medical & First Aid Room', 15, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_012', 'Administrative Block Foyer', 'Campus Central Elevator', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_013', 'Security Cabin', 'PU College Stairs', 18, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_014', 'Administrative Block Foyer', 'PU College Stairs', 15, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_015', 'PU College Stairs', 'Reprography Room', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_016', 'Reprography Room', 'Mushroom Cultivation Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_017', 'Mushroom Cultivation Lab', 'Golden Jubilee Seminar Hall', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_018', 'PU College Stairs', 'Golden Jubilee Seminar Hall', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_019', 'PU College Stairs', 'Xerox & Stationery Kiosk', 10, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_020', 'Golden Jubilee Seminar Hall', 'Classroom G1', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_021', 'Classroom G1', 'Classroom G2', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_022', 'Classroom G2', 'Classroom G3', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_023', 'Classroom G3', 'Classroom G4', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_024', 'Classroom G4', 'Classroom G5', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_025', 'Classroom G5', 'Classroom G6', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_026', 'Classroom G6', 'Classroom G7', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_027', 'Classroom G7', 'Classroom G8', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_028', 'Classroom G8', 'Classroom G9', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_029', 'Classroom G9', 'Classroom G10', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_030', 'Classroom G10', 'Classroom G11', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_031', 'Classroom G11', 'Controller of Examination', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_032', 'Controller of Examination', 'Sports & Gym', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_033', 'Sports & Gym', 'South Staircase', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_034', 'South Staircase', 'Girls Washroom', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_035', 'Sports & Gym', 'Canteen Area', 18, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_036', 'Girls Washroom', 'Canteen Area', 15, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_037', 'Security Cabin', 'College Garden Walkway', 15, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_038', 'Administrative Block Foyer', 'College Garden Walkway', 15, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_039', 'College Garden Walkway', 'Canteen Area', 30, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_040', 'Canteen Area', 'Canteen Kitchen', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_041', 'Main Reception Staircase', 'Main Reception Staircase (Floor 1)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_042', 'PU College Stairs', 'PU College Stairs (Floor 1)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_043', 'South Staircase', 'South Staircase (Floor 1)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_044', 'Campus Central Elevator', 'Campus Central Elevator (Floor 1)', 12, 'Elevator', TRUE, 'Low', 'Vertical'),
('P_045', 'Main Reception Staircase (Floor 1)', 'Campus Central Elevator (Floor 1)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_046', 'Main Reception Staircase (Floor 1)', 'Classroom F4', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_047', 'Main Reception Staircase (Floor 1)', 'Classroom F1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_048', 'Main Reception Staircase (Floor 1)', 'PU College Stairs (Floor 1)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_049', 'Main Reception Staircase (Floor 1)', 'Biotechnology Lab (PG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_050', 'Main Reception Staircase (Floor 1)', 'Dept. of Botany', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_051', 'PU College Stairs (Floor 1)', 'Campus Central Elevator (Floor 1)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_052', 'Campus Central Elevator (Floor 1)', 'Biotechnology Lab (PG)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_053', 'PU College Stairs (Floor 1)', 'Biotechnology Lab (PG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_054', 'Biotechnology Lab (PG)', 'Biotechnology Lab (UG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_055', 'PU College Stairs (Floor 1)', 'Faculty Washroom (First Floor)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_056', 'PU College Stairs (Floor 1)', 'Classroom F4', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_057', 'Campus Central Elevator (Floor 1)', 'Classroom F4', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_058', 'Classroom F4', 'Classroom F3', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_059', 'Classroom F3', 'Classroom F2', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_060', 'Classroom F2', 'Dept. of Botany', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_061', 'Classroom F2', 'Classroom F1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_062', 'Classroom F3', 'Classroom F1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_063', 'Dept. of Botany', 'Dept. of Journalism', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_064', 'Dept. of Botany', 'Botany Lab (PG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_065', 'Dept. of Journalism', 'Botany Lab (PG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_066', 'Botany Lab (PG)', 'Botany Lab (UG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_067', 'Botany Lab (UG)', 'Microbiology Lab (Floor 1)', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_068', 'Microbiology Lab (Floor 1)', 'Classroom F5', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_069', 'Classroom F5', 'Physics Lab III', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_070', 'Physics Lab III', 'Dept. of Physics (UG) & Faculty Chamber', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_071', 'Dept. of Physics (UG) & Faculty Chamber', 'Physics Lab II', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_072', 'Physics Lab II', 'Dept. of Physics (PU)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_073', 'Dept. of Physics (PU)', 'Physics Lab I', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_074', 'Physics Lab I', 'South Staircase (Floor 1)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_075', 'South Staircase (Floor 1)', 'Floor 1 Student Washroom', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_076', 'Floor 1 Student Washroom', 'Dept. of Chemistry & Staff Room', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_077', 'South Staircase (Floor 1)', 'Dept. of Chemistry & Staff Room', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_078', 'Dept. of Chemistry & Staff Room', 'Chemistry Lab I', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_079', 'Chemistry Lab I', 'Chemistry Research Centre', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_080', 'Chemistry Research Centre', 'Chemistry Lab II', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_081', 'Chemistry Lab II', 'Chemistry Lab III', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_082', 'Chemistry Lab III', 'Biochemistry Lab (PG)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_083', 'Biochemistry Lab (PG)', 'Dept. of Life Sciences Staff Room', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_084', 'Dept. of Life Sciences Staff Room', 'Zoology Lab (UG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_085', 'Zoology Lab (UG)', 'Biotechnology Lab (UG)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_086', 'Main Reception Staircase (Floor 1)', 'Main Reception Staircase (Floor 2)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_087', 'PU College Stairs (Floor 1)', 'PU College Stairs (Floor 2)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_088', 'South Staircase (Floor 1)', 'South Staircase (Floor 2)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_089', 'Campus Central Elevator (Floor 1)', 'Campus Central Elevator (Floor 2)', 12, 'Elevator', TRUE, 'Low', 'Vertical'),
('P_090', 'PU College Stairs (Floor 2)', 'Classroom S1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_091', 'Classroom S1', 'Classroom S2', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_092', 'Classroom S2', 'Classroom S3', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_093', 'Classroom S3', 'Floor 2 West Restroom', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_094', 'Floor 2 West Restroom', 'Campus Central Elevator (Floor 2)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_095', 'Classroom S3', 'Campus Central Elevator (Floor 2)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_096', 'PU College Stairs (Floor 2)', 'Campus Central Elevator (Floor 2)', 14, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_097', 'Campus Central Elevator (Floor 2)', 'Central Library', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_098', 'Central Library', 'Mathematics Department', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_099', 'Central Library', 'Classroom S4', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_100', 'Classroom S4', 'Classroom S5', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_101', 'Classroom S5', 'Floor 2 North Apex Restroom', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_102', 'Floor 2 North Apex Restroom', 'North-East Staircase (Floor 2)', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_103', 'North-East Staircase (Floor 2)', 'Classroom S6', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_104', 'Classroom S6', 'Classroom S7', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_105', 'Classroom S7', 'Computer Lab 1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_106', 'Computer Lab 1', 'Dept. of Computer Science & Staff Room', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_107', 'Dept. of Computer Science & Staff Room', 'Classroom S8', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_108', 'Classroom S8', 'Computer Lab 2', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_109', 'Computer Lab 2', 'Electronics & Hardware Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_110', 'Electronics & Hardware Lab', 'Language Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_111', 'Language Lab', 'Dept. of Commerce & Management (BBA)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_112', 'Dept. of Commerce & Management (BBA)', 'KNV Shastri Auditorium', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_113', 'KNV Shastri Auditorium', 'South Staircase (Floor 2)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_114', 'Classroom S1', 'Classroom S9', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_115', 'PU College Stairs (Floor 2)', 'Classroom S9', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_116', 'Classroom S9', 'Classroom S10', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_117', 'Classroom S10', 'Classroom S11', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_118', 'Classroom S11', 'Classroom S12', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_119', 'Classroom S12', 'Main Reception Staircase (Floor 2)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_120', 'Main Reception Staircase (Floor 2)', 'Dept. of Commerce & Management (BBA)', 15, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_121', 'Main Reception Staircase (Floor 2)', 'South Staircase (Floor 2)', 18, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_122', 'Campus Central Elevator (Floor 2)', 'Classroom S9', 16, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_123', 'Campus Central Elevator (Floor 2)', 'Main Reception Staircase (Floor 2)', 20, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_124', 'Campus Central Elevator (Floor 2)', 'Campus Central Elevator (Floor 3)', 12, 'Elevator', TRUE, 'Low', 'Vertical'),
('P_125', 'PU College Stairs (Floor 2)', 'PU College Stairs (Floor 3)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_126', 'South Staircase (Floor 2)', 'South Staircase (Floor 3)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_127', 'North-East Staircase (Floor 2)', 'North-East Staircase (Floor 3)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_128', 'Main Reception Staircase (Floor 2)', 'Main Reception Staircase (Floor 3)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_129', 'PU College Stairs (Floor 3)', 'Animal Cell Culture Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_130', 'Animal Cell Culture Lab', 'Life Science Research Centre', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_131', 'Life Science Research Centre', 'Classroom PG T1', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_132', 'Classroom PG T1', 'Campus Central Elevator (Floor 3)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_133', 'PU College Stairs (Floor 3)', 'Campus Central Elevator (Floor 3)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_134', 'Campus Central Elevator (Floor 3)', 'Library (PG)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_135', 'Main Reception Staircase (Floor 3)', 'Student Open Lounge (Third Floor Level)', 6, 'Open Walkway', TRUE, 'Low', 'Horizontal'),
('P_136', 'Campus Central Elevator (Floor 3)', 'Student Open Lounge (Third Floor Level)', 14, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_137', 'Student Open Lounge (Third Floor Level)', 'Third Floor Lecture Hall', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_138', 'North-East Staircase (Floor 3)', 'Third Floor Lecture Hall', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_139', 'Third Floor Lecture Hall', 'Business Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_140', 'Business Lab', 'Dept. of Commerce (UG & PG)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_141', 'Dept. of Commerce (UG & PG)', 'Dept. of Commerce Research Centre & UGC Centre', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_142', 'Dept. of Commerce Research Centre & UGC Centre', 'DBT-Bioinformatics Facility', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_143', 'DBT-Bioinformatics Facility', 'South Staircase (Floor 3)', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_144', 'Student Open Lounge (Third Floor Level)', 'Dept. of Commerce (UG & PG)', 14, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_145', 'Administrative Block Foyer', 'Fee Counters', 15, 'Corridor', TRUE, 'Medium', 'Horizontal'),
('P_146', 'Fee Counters', 'Central Library', 10, 'Corridor', TRUE, 'Medium', 'Horizontal'),
('P_147', 'Central Library', 'Smritimaya mLAC Museum', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_148', 'Smritimaya mLAC Museum', 'Main Reception Staircase', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_149', 'Classroom G8', 'Dept. of Psychology', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_150', 'Dept. of Psychology', 'Classroom G9', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_151', 'Classroom G11', 'Dept. of English, Hindi & Sanskrit', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_152', 'Canteen Area', 'Health Centre', 14, 'Paved Walkway', TRUE, 'Low', 'Horizontal'),
('P_153', 'Health Centre', 'Gents Washroom', 12, 'Paved Walkway', TRUE, 'Low', 'Horizontal'),
('P_154', 'Gents Washroom', 'mLAC Garden', 15, 'Paved Walkway', TRUE, 'Low', 'Horizontal'),
('P_155', 'mLAC Garden', 'College Garden Walkway', 10, 'Paved Walkway', TRUE, 'Low', 'Horizontal'),
('P_156', 'Classroom PG T1', 'Library (PG)', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_157', 'Library (PG)', 'Classroom PG T2 & T3', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_158', 'Classroom PG T2 & T3', 'Campus Central Elevator (Floor 3)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_159', 'Third Floor Lecture Hall', 'mLAC - KSCST - IP Cell (PG T7)', 10, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_160', 'mLAC - KSCST - IP Cell (PG T7)', 'Classroom PG T5 & T6', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_161', 'Classroom PG T5 & T6', '1 KAR Air SQN NCC & NCC Store', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_162', 'Main Reception Staircase (Floor 3)', 'Classroom PG T8', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_163', 'Classroom PG T8', 'Business Lab', 8, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_164', 'DBT-Bioinformatics Facility', 'Third Floor Lecture Hall', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_165', '1 KAR Air SQN NCC & NCC Store', 'Student Open Lounge (Third Floor Level)', 8, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_166', 'Student Open Lounge (Third Floor Level)', 'Girls Wash Room (Student Lounge)', 6, 'Hall', TRUE, 'Low', 'Horizontal'),
('P_167', 'Student Open Lounge (Third Floor Level)', 'Green Room (Student Lounge)', 8, 'Hall', TRUE, 'Low', 'Horizontal'),
('P_168', 'Classroom S12', 'Student Open Lounge (Third Floor Level)', 12, 'Stairs', FALSE, 'Low', 'Vertical'),
('P_169', 'Life Science Research Centre', 'Biotechnology Research Lab', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_170', 'Biotechnology Research Lab', 'Classroom PG T1', 6, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_171', 'Dept. of Commerce & Management (BBA)', 'Dept. of Computer Science & Staff Room', 12, 'Corridor', TRUE, 'Low', 'Horizontal'),
('P_172', 'Main Reception Staircase', 'Classroom G11', 18, 'Quadrangle Pathway', TRUE, 'Low', 'Horizontal');
