import sys
import os
import gallery_dl.config as config
import gallery_dl.job as job
import logging

def test_gdl():
    # Setup dummy logging
    logging.basicConfig(level=logging.INFO)
    
    config.load()
    # config.set((), "base-directory", "D:\\FB DL\\downloads")
    # config.set(("postprocessor", "cbz"), "extension", "cbz")
    # config.set(("extractor",), "postprocessors", [{"name": "cbz"}])
    
    print("Testing gallery-dl API")
    try:
        j = job.DownloadJob("https://www.facebook.com/photo/?fbid=10156942469490195")
        res = j.run()
        print("Result:", res)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    test_gdl()
