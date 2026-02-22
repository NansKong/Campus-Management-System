import cv2
import face_recognition
import numpy as np
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from app.models.student import Student
from app.models.course import SectionEnrollment
import json
import base64
from PIL import Image
import io

class FaceRecognitionService:
    """Service for AI-based face recognition attendance"""
    
    @staticmethod
    def encode_face_from_image(image_path: str) -> List[float]:
        """
        Extract face encoding from an image
        Returns: List of 128 facial features
        """
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Detect faces
            face_locations = face_recognition.face_locations(image)
            
            if len(face_locations) == 0:
                raise ValueError("No face detected in the image")
            
            if len(face_locations) > 1:
                raise ValueError("Multiple faces detected. Please upload image with single face")
            
            # Get face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            if len(face_encodings) > 0:
                return face_encodings[0].tolist()
            else:
                raise ValueError("Could not encode face")
                
        except Exception as e:
            raise Exception(f"Face encoding error: {str(e)}")
    
    @staticmethod
    def enroll_student_face(db: Session, student_id: str, image_path: str) -> Dict:
        """
        Enroll a student's face for recognition
        """
        try:
            # Get face encoding
            face_encoding = FaceRecognitionService.encode_face_from_image(image_path)
            
            # Store in database
            student = db.query(Student).filter(Student.student_id == student_id).first()
            
            if not student:
                raise ValueError("Student not found")
            
            # Convert encoding to JSON string
            encoding_json = json.dumps(face_encoding)
            student.face_encoding = encoding_json
            
            db.commit()
            
            return {
                "success": True,
                "message": "Face enrolled successfully",
                "student_id": student_id
            }
            
        except Exception as e:
            raise Exception(f"Enrollment error: {str(e)}")
    
    @staticmethod
    def mark_attendance_from_image(db: Session, section_id: str, image_path: str, 
                                   confidence_threshold: float = 0.6) -> Dict:
        """
        Mark attendance by detecting faces in class photo
        
        Args:
            db: Database session
            section_id: Course section ID
            image_path: Path to class photo
            confidence_threshold: Minimum confidence for face match (0-1)
            
        Returns:
            Dictionary with attendance results
        """
        try:
            # Load class image
            image = face_recognition.load_image_file(image_path)
            
            # Detect all faces in the image
            face_locations = face_recognition.face_locations(image, model='hog')
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            print(f"Detected {len(face_locations)} faces in the image")
            
            # Get all enrolled students in this section
            enrollments = db.query(SectionEnrollment).filter(
                SectionEnrollment.section_id == section_id,
                SectionEnrollment.status == 'active'
            ).all()
            
            # Get students with face encodings
            enrolled_students = []
            known_encodings = []
            
            for enrollment in enrollments:
                student = db.query(Student).filter(
                    Student.student_id == enrollment.student_id
                ).first()
                
                if student and student.face_encoding:
                    enrolled_students.append(student)
                    # Parse JSON encoding
                    encoding = json.loads(student.face_encoding)
                    known_encodings.append(np.array(encoding))
            
            print(f"Found {len(enrolled_students)} students with face encodings")
            
            # Match faces
            present_students = []
            unrecognized_faces = 0
            
            for face_encoding in face_encodings:
                # Compare with all known faces
                if len(known_encodings) == 0:
                    unrecognized_faces += 1
                    continue
                
                # Calculate face distances
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                
                # Find best match
                best_match_index = np.argmin(face_distances)
                best_distance = face_distances[best_match_index]
                
                # Convert distance to confidence (inverse relationship)
                confidence = 1 - best_distance
                
                print(f"Best match confidence: {confidence:.2f}")
                
                if confidence >= confidence_threshold:
                    matched_student = enrolled_students[best_match_index]
                    
                    # Avoid duplicates
                    if matched_student.student_id not in [s['student_id'] for s in present_students]:
                        present_students.append({
                            'student_id': str(matched_student.student_id),
                            'name': f"{matched_student.first_name} {matched_student.last_name}",
                            'registration_number': matched_student.registration_number,
                            'confidence': round(confidence * 100, 2)
                        })
                else:
                    unrecognized_faces += 1
            
            return {
                'success': True,
                'total_faces_detected': len(face_locations),
                'students_recognized': len(present_students),
                'unrecognized_faces': unrecognized_faces,
                'present_students': present_students,
                'message': f'Recognized {len(present_students)} out of {len(face_locations)} faces detected'
            }
            
        except Exception as e:
            raise Exception(f"Face recognition error: {str(e)}")
    
    @staticmethod
    def process_base64_image(base64_string: str) -> str:
        """
        Convert base64 image to file and return path
        """
        try:
            # Remove data:image prefix if present
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]
            
            # Decode base64
            image_data = base64.b64decode(base64_string)
            
            # Save to temporary file
            temp_path = f"/tmp/class_photo_{np.random.randint(1000, 9999)}.jpg"
            
            with open(temp_path, 'wb') as f:
                f.write(image_data)
            
            return temp_path
            
        except Exception as e:
            raise Exception(f"Image processing error: {str(e)}")

face_recognition_service = FaceRecognitionService()