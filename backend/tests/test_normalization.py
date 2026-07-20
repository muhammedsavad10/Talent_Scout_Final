import pytest
from app.agents.normalization import normalize_skill, normalize_skills_list, normalize_unicode, split_camel_case

def test_alias_resolution():
    assert normalize_skill("FastAPI") == "FastAPI"
    assert normalize_skill("FASTAPI") == "FastAPI"
    assert normalize_skill("fast-api") == "FastAPI"
    assert normalize_skill("reactjs") == "ReactJS"
    assert normalize_skill("React.js") == "ReactJS"

def test_camelcase_splitting():
    # If it's a known alias, it shouldn't split
    assert normalize_skill("ReactJS") == "ReactJS"
    # If it's unknown, it should split
    assert normalize_skill("MachineLearning") == "Machine Learning"
    assert split_camel_case("DeepLearning") == "Deep Learning"

def test_duplicate_removal():
    skills = ["FastAPI", "fastapi", "fast-api", "Python", "python"]
    normalized = normalize_skills_list(skills)
    assert len(normalized) == 2
    assert set(normalized) == {"FastAPI", "Python"}

def test_unicode_normalization():
    # 'e' with acute accent
    accented_e = "r\u00e9sum\u00e9"
    normalized = normalize_unicode(accented_e)
    assert normalized == "resume"
    
    assert normalize_skill("Caf\u00e9") == "Cafe"
