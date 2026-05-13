import time 
 
def _analyze_with_schema_with_retry(self, prompt: str, image_part, schema: dict): 
    for attempt in range(4): 
        try: 
            return self.client.models.generate_content(model=self.model_name, contents=[prompt, image_part], config=self._build_generation_config(schema)) 
        except Exception as e: 
            if '429' in str(e) or 'RESOURCE_EXHAUSTED' in str(e): 
                wait_time = 10 * (2 ** attempt) 
                print(f'Rate limit hit (429). Waiting {wait_time} seconds before retry...') 
                time.sleep(wait_time) 
                if attempt == 3: 
                    raise e 
            else: 
                raise e
