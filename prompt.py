def get_prompt(target_language: str, source_language: str):
    prompt = f"""Translate the text in this {source_language} marketing product image to {target_language}. Text position stays where it is and don't touch anything else other than text. Critical: Only the text should be translated in {target_language} for the output image nothing else changes.CRITICAL WARNING - NEVER SQUASH OR DISTORT Image Chunk's own ratio.Don't trim or crop any part of the image. But you can chunk the long image to sides if you want. e.g. Don't squash the character or item to lose its original ratio. Don't add any extra texts if there wasn't any text there. Don't ruin the original design other than texts.
    
    [CRITICAL: ASPECT RATIO PRESERVATION]
1. DO NOT stretch, squash, or distort the image in any way. 
2. Every image chunk must maintain its original width-to-height ratio (Aspect Ratio).
3. If you place chunks side-by-side, do not resize them to fit a specific frame. Instead, place them on a larger canvas with neutral padding (white background) if necessary to prevent distortion. 
4. The physical proportions of the products and people must remain identical to the source.
"""
    return prompt
