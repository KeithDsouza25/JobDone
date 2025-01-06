import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from collections import Counter

class ScoreCalculator:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        # Keywords that indicate important requirements
        self.importance_markers = [
            'required', 'requirements', 'must have', 'essential', 'necessary',
            'qualification', 'experience', 'skill', 'proficiency', 'expertise',
            'background', 'knowledge', 'ability', 'capable', 'proficient'
        ]
        
        # Common technical skills and qualifications
        self.skill_patterns = [
            r'[A-Za-z0-9]+\+{0,1}[\s]*(?:years|yrs)',  # Experience patterns like "5+ years"
            r'bachelor|master|phd|degree|certification',  # Education
            r'[A-Za-z0-9#\+\+]+(?:\.[A-Za-z0-9]+)*',   # Programming languages and tools
        ]

    def extract_key_requirements(self, job_desc):
        doc = self.nlp(job_desc.lower())
        
        # Find sentences with importance markers
        important_sentences = []
        for sent in doc.sents:
            if any(marker in sent.text.lower() for marker in self.importance_markers):
                important_sentences.append(sent.text)
        
        # Extract key terms from important sentences
        key_terms = []
        for sent in important_sentences:
            # Extract years of experience
            experience_matches = re.findall(r'\d+\+?\s*(?:years?|yrs?)', sent)
            key_terms.extend(experience_matches)
            
            # Extract other important terms
            doc_sent = self.nlp(sent)
            for token in doc_sent:
                if (token.pos_ in ['NOUN', 'PROPN'] and 
                    len(token.text) > 2 and 
                    not token.is_stop):
                    key_terms.append(token.text)
        
        return list(set(key_terms))

    def calculate_score(self, resume_text, job_desc_text):
        # Extract key requirements
        key_requirements = self.extract_key_requirements(job_desc_text)
        
        # Calculate base score from key requirements
        resume_text_lower = resume_text.lower()
        matches = 0
        total_reqs = len(key_requirements)
        
        # Weighted scoring for requirements
        for req in key_requirements:
            req_lower = req.lower()
            # Give full point for exact matches
            if req_lower in resume_text_lower:
                matches += 1.5  # Increased bonus points for exact matches
            # Give partial points for partial matches
            else:
                # Split requirement into words and check each
                req_words = req_lower.split()
                if len(req_words) > 1:  # Only for multi-word requirements
                    matched_words = sum(1 for word in req_words 
                                     if word in resume_text_lower and len(word) > 3)
                    matches += (matched_words / len(req_words)) * 1.2  # Increased partial match points
        
        # Base score from key requirements (80% of total score)
        base_score = (matches / total_reqs) * 8.0 if total_reqs > 0 else 0
        
        # Calculate similarity score for overall content (20% of total score)
        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_desc_text])
            similarity_score = ((tfidf_matrix * tfidf_matrix.T).A[0][1]) * 2.0
            # Boost similarity score if it's above average
            if similarity_score > 1.0:  # Further lowered threshold
                similarity_score *= 1.4  # Increased boost
        except:
            similarity_score = 0
        
        # Combine scores
        final_score = base_score + similarity_score
        
        # Apply an even more generous curve to boost scores
        if final_score > 4:  # Lowered threshold further
            final_score *= 1.3  # Increased boost
        elif final_score > 2:  # Lowered threshold further
            final_score *= 1.25
        
        # Add a higher minimum score floor for any reasonable match
        if final_score > 0:
            final_score = max(final_score, 7.0)  # Increased minimum score to 7.0
        
        # Ensure score is between 0 and 10
        final_score = min(max(final_score, 0), 10)
        
        # Round to one decimal place
        return round(final_score, 1)