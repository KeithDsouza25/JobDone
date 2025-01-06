import streamlit as st
from jobdone.file_processor.pdf_reader import PDFReader
from jobdone.file_processor.docx_reader import DocxReader
from jobdone.file_processor.text_reader import TextReader
from jobdone.analyzers.score_calculator import ScoreCalculator
from jobdone.analyzers.word_cloud_generator import WordCloudGenerator
from jobdone.analyzers.keyword_matcher import KeywordMatcher
from jobdone.resume_generator.ai_generator import ResumeGenerator
import re

def set_page_config():
    st.set_page_config(
        page_title="JobDone.AI Resume Analyzer",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'mailto:kdmusic2509@gmail.com',
            'Report a bug': 'mailto:kdmusic2509@gmail.com',
            'About': '''
            ## JobDone.AI Resume Analyzer
            An AI-powered tool to optimize your resume for job applications.
            
            Version: 1.0.0
            Contact: kdmusic2509@gmail.com
            '''
        }
    )

def load_css():
    try:
        with open('app/static/css/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback path for when running from streamlit cloud
        with open('static/css/style.css') as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

class ResumeBuilderApp:
    def __init__(self):
        self.supported_formats = ['.pdf', '.docx', '.txt']
        
    def run(self):
        set_page_config()
        load_css()
        
        # Update to use st.query_params instead of experimental_get_query_params
        page = st.query_params.get("page", "home")
        
        if page == "services":
            self.show_services_page()
        elif page == "about":
            self.show_about_page()
        else:
            self.show_main_page()

    def show_services_page(self):
        st.markdown('<h1 class="main-title">Our Services</h1>', unsafe_allow_html=True)
        # Add your services content here

    def show_about_page(self):
        st.markdown('<h1 class="main-title">About Us</h1>', unsafe_allow_html=True)
        # Add your about content here

    def show_main_page(self):
        # Your existing main page content
        st.markdown('<h1 class="main-title">Resume Analyzer</h1>', unsafe_allow_html=True)
        st.markdown('<h3 class="subtitle">Optimize your resume for your dream job</h3>', unsafe_allow_html=True)
        
        # Create two columns with spacing
        col1, space, col2 = st.columns([4, 1, 4])
        
        with col1:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.markdown('<p class="upload-label">📄 Upload Resume</p>', unsafe_allow_html=True)
            
            # File upload option first
            resume_file = st.file_uploader("Upload resume file", type=self.supported_formats, key="resume")
            
            # Text area below file upload
            st.markdown('<p class="text-label">Or paste resume text here:</p>', unsafe_allow_html=True)
            resume_text_input = st.text_area("", height=200, key="resume_text", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            st.markdown('<p class="upload-label">📋 Upload Job Description</p>', unsafe_allow_html=True)
            
            # File upload option first
            job_desc_file = st.file_uploader("Upload job description file", type=self.supported_formats, key="job_desc")
            
            # Text area below file upload
            st.markdown('<p class="text-label">Or paste job description here:</p>', unsafe_allow_html=True)
            job_desc_text_input = st.text_area("", height=200, key="job_desc_text", label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)

        # Update the processing logic to handle both file and text input
        resume_text = ""
        job_desc_text = ""
        
        if resume_file:
            resume_text = self._process_file(resume_file)
        elif resume_text_input:
            resume_text = resume_text_input
            
        if job_desc_file:
            job_desc_text = self._process_file(job_desc_file)
        elif job_desc_text_input:
            job_desc_text = job_desc_text_input

        # After the job description input section
        if (resume_text and job_desc_text):
            if 'analysis_done' not in st.session_state:
                st.session_state.analysis_done = False
            
            # Add space before analyze button
            st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
            
            # Center the analyze button    
            col1, col2, col3 = st.columns([3, 2, 3])
            with col2:
                analyze_button = st.button("🔍 Analyze Resume Match", use_container_width=True)
            
            if analyze_button:
                st.session_state.analysis_done = True
            
            if st.session_state.analysis_done:
                st.markdown("---")
                
                # Analysis results in columns
                col1, col2 = st.columns(2)
                
                with col1:
                    score_calculator = ScoreCalculator()
                    match_score = score_calculator.calculate_score(resume_text, job_desc_text)
                    st.markdown(f"""
                        <div style='padding: 0.5rem;'>
                            <h2 style='color: #0066cc; margin-bottom: 0.5rem; font-size: 1.2rem;'>Match Score</h2>
                            <h1 style='font-size: 2.5rem; font-weight: bold; color: #1f1f1f;'>{match_score}/10</h1>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    keyword_matcher = KeywordMatcher()
                    matching_keywords = keyword_matcher.find_matches(resume_text, job_desc_text)
                    st.write("#### Matching Keywords")
                    st.write(", ".join(matching_keywords['found']))
                
                with col2:
                    word_cloud = WordCloudGenerator()
                    # Extract important information before generating word cloud
                    important_patterns = {
                        'years_exp': r'\b(\d+[\+]?\s*-?\s*\d*)\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)\b',
                        'location': r'\b(?:in|at|from)?\s*((?:remote|hybrid|onsite|on-site|in-office))\b|\b([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?)\b',
                        'skills': r'\b(?:Python|Java|JavaScript|React|AWS|SQL|Docker|Kubernetes|Azure|Git|REST|API|ML|AI|Node\.js|TypeScript|Angular|Vue\.js|PHP|C\+\+|Swift|Kotlin|Ruby|Go|Rust|HTML|CSS|MongoDB|PostgreSQL|MySQL)\b',
                        'education': r'\b(?:Bachelor\'?s?|Master\'?s?|PhD|BS|MS|BA|MBA|MD)\b',
                        'salary': r'\$\s*(?:\d{1,3},)*\d{1,3}(?:k|K)?\s*(?:-\s*\$\s*(?:\d{1,3},)*\d{1,3}(?:k|K)?)?(?:\s*\/\s*(?:year|yr|month|mo|annual|annually))?'
                    }
                    
                    # Create columns for important information
                    st.write("#### Key Job Requirements")
                    info_col1, info_col2 = st.columns(2)
                    
                    with info_col1:
                        # Extract and display experience
                        exp_matches = re.findall(important_patterns['years_exp'], job_desc_text, re.IGNORECASE)
                        if exp_matches:
                            st.write("🎯 **Experience:** ", exp_matches[0], "years")
                        
                        # Improved location detection
                        location_pattern = r'\b(?:remote|hybrid|on-site|onsite)\b|\b[A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2})?\b|\b[A-Z]{2},\s*USA\b|\b(?:United States|Canada|UK|Australia|New Zealand|India)\b'
                        loc_matches = re.findall(location_pattern, job_desc_text)
                        
                        location = "Unknown"
                        if loc_matches:
                            # Prioritize 'remote' if it exists
                            if any(word.lower() == 'remote' for word in loc_matches):
                                location = "Remote"
                            else:
                                # Take the first location match that's not a work arrangement
                                for match in loc_matches:
                                    if match.lower() not in ['hybrid', 'on-site', 'onsite']:
                                        location = match
                                        break
                        
                        st.write("📍 **Location:** ", location)
                    
                    with info_col2:
                        # Extract and display salary if available
                        salary_matches = re.findall(important_patterns['salary'], job_desc_text)
                        if salary_matches:
                            st.write("💰 **Salary:** ", salary_matches[0])
                        
                        # Extract and display required education
                        edu_matches = re.findall(important_patterns['education'], job_desc_text)
                        if edu_matches:
                            st.write("🎓 **Education:** ", edu_matches[0])
                    
                    # Extract skills and give them higher weight in word cloud
                    skills = re.findall(important_patterns['skills'], job_desc_text)
                    
                    # Generate word cloud with higher weights for important terms
                    word_cloud_image = word_cloud.generate(job_desc_text)
                    st.image(word_cloud_image, caption="Important Keywords in Job Description")
                
                # Add space before generate resume button
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                
                # Center the generate resume button
                col1, col2, col3 = st.columns([3, 2, 3])
                with col2:
                    if st.button("Generate Optimized Resume", use_container_width=True):
                        with st.spinner("Generating optimized resume..."):
                            resume_gen = ResumeGenerator()
                            optimized_resume = resume_gen.generate(resume_text, job_desc_text)
                            st.download_button(
                                "📥 Download Optimized Resume",
                                optimized_resume,
                                file_name="optimized_resume.docx",
                                use_container_width=True
                            )

    def _process_file(self, file):
        file_ext = file.name.split('.')[-1].lower()
        if file_ext == 'pdf':
            return PDFReader().read(file)
        elif file_ext == 'docx':
            return DocxReader().read(file)
        else:
            return TextReader().read(file)

if __name__ == "__main__":
    app = ResumeBuilderApp()
    app.run()