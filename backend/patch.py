import re  
with open('retry_inject.py') as f: retry_str = f.read().replace('def _analyze_with_schema_with_retry', 'def _analyze_with_schema')  
with open('apps/skincare_analysis/gemini_client.py', 'r') as f2: client_code = f2.read()  
new_code = re.sub(r'def _analyze_with_schema\(self, prompt.*?\n        \)', retry_str, client_code, flags=re.DOTALL)  
with open('apps/skincare_analysis/gemini_client.py', 'w') as f3: f3.write(new_code)  
