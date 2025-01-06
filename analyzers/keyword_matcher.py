import spacy
from collections import Counter

class KeywordMatcher:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
    
    def find_matches(self, resume_text, job_desc_text):
        # Process texts
        job_doc = self.nlp(job_desc_text.lower())
        resume_doc = self.nlp(resume_text.lower())
        
        # Extract important keywords from job description
        job_keywords = [token.text for token in job_doc 
                       if not token.is_stop and not token.is_punct and token.pos_ in ['NOUN', 'PROPN', 'ADJ']]
        
        # Count frequency of important keywords
        keyword_freq = Counter(job_keywords)
        important_keywords = {word: count for word, count in keyword_freq.items() if count > 1}
        
        # Find matches in resume
        resume_words = set([token.text for token in resume_doc 
                          if not token.is_stop and not token.is_punct])
        
        matches = {
            'found': [word for word in important_keywords if word in resume_words],
            'missing': [word for word in important_keywords if word not in resume_words]
        }
        
        return matches