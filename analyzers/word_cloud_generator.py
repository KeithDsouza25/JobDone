from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64

class WordCloudGenerator:
    def generate(self, text):
        # Create and generate a word cloud image
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
        
        # Create the image
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Save it to a temporary buffer.
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return buf