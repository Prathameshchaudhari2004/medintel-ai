# utils/knowledge_base.py
# --------------------------------------------------
# This module provides two things:
#
# 1. Plain-language explanations for abnormal test results
#    (so patients understand what their values mean)
#
# 2. Diet & lifestyle recommendations based on what's
#    wrong with their blood work
#
# The goal is to sound like a knowledgeable friend
# explaining things simply — not like a textbook.
# --------------------------------------------------


# --------------------------------------------------
# MEDICAL EXPLANATIONS
#
# Each parameter has explanations for "Low", "High",
# and "Critical" statuses.
# --------------------------------------------------
EXPLANATIONS = {
    "Hemoglobin": {
        "Low": """
Your hemoglobin is lower than the normal range. Hemoglobin is the protein in your red blood cells that carries oxygen from your lungs to the rest of your body.

**What this might mean:**
- Iron deficiency anemia (most common cause — happens when you don't have enough iron)
- Vitamin B12 or folate deficiency
- Chronic disease or kidney problems
- In women: heavy menstrual periods

**Common symptoms you might feel:**
- Tiredness and weakness
- Shortness of breath, especially during exercise
- Dizziness or lightheadedness
- Pale skin
- Headaches

**What to do:**
- Visit your doctor to find the exact cause
- Eat more iron-rich foods (red meat, spinach, lentils, beans)
- Take iron supplements only if your doctor recommends them
- Vitamin C helps your body absorb iron better
        """,
        "High": """
Your hemoglobin is higher than normal. While this is less common than low hemoglobin, it can be a sign of certain conditions.

**What this might mean:**
- Living at high altitude (your body makes more hemoglobin to cope with less oxygen)
- Dehydration (blood becomes more concentrated)
- Smoking (a very common cause)
- Rarely, a bone marrow condition called polycythemia vera

**What to do:**
- Drink more water to rule out dehydration
- If you smoke, this is another reason to quit
- See your doctor for a proper evaluation
        """,
        "Critical": """
🚨 **Your hemoglobin is at a critical level.** This is an urgent medical situation.

Please go to a hospital or emergency care immediately. At this level, your body's organs are not getting enough oxygen, which is dangerous.

Do not delay seeking medical attention.
        """
    },

    "Glucose": {
        "Low": """
Your blood glucose (blood sugar) is below normal. This condition is called hypoglycemia.

**What this might mean:**
- You haven't eaten for a long time (fasted too long)
- Side effect of diabetes medication (if you're on any)
- Liver problems
- Hormonal issues

**Symptoms to watch for:**
- Shakiness, trembling
- Sweating and anxiety
- Rapid heartbeat
- Confusion or difficulty thinking
- Extreme hunger

**Immediate action:**
- Eat something sweet right away (juice, candy, glucose tablets)
- Then eat a proper meal with complex carbs
- If symptoms are severe, go to emergency care
        """,
        "High": """
Your blood glucose is higher than normal. This is called hyperglycemia.

**Normal fasting range: 70-100 mg/dL**
**Pre-diabetes range: 100-125 mg/dL**
**Diabetes range: 126 mg/dL and above**

**What this might mean:**
- Pre-diabetes or Type 2 diabetes (most common)
- You ate a large meal just before the test
- High stress or illness
- Certain medications

**What you should do:**
- Get an HbA1c test to check your 3-month average sugar
- Reduce sugary foods, white rice, bread, and maida
- Exercise regularly — even a 30-minute walk helps a lot
- See a doctor — early intervention can prevent diabetes
        """,
        "Critical": """
🚨 **Critically high blood sugar.** This requires immediate medical attention.

At this level, you're at risk for diabetic ketoacidosis (DKA) or hyperosmolar hyperglycemic state — both are medical emergencies.

Please go to the hospital immediately.
        """
    },

    "Cholesterol": {
        "High": """
Your total cholesterol is above the recommended level. Cholesterol is a fatty substance in your blood, and having too much of it increases the risk of heart disease.

**Categories:**
- Under 200 mg/dL — Desirable
- 200-239 mg/dL — Borderline high
- 240 mg/dL and above — High

**What this might mean:**
- Diet high in saturated and trans fats
- Lack of physical activity
- Genetics (some people naturally have higher cholesterol)
- Thyroid problems

**What you should do:**
- Reduce fried foods, processed snacks, and red meat
- Eat more oats, nuts, fish, and olive oil
- Exercise at least 150 minutes per week
- See your doctor — they may recommend medication (statins) if lifestyle changes aren't enough
        """,
        "Critical": """
🚨 **Very high cholesterol.** Your risk of heart attack and stroke is significantly elevated.

Please consult a cardiologist as soon as possible. You will likely need both medication and significant lifestyle changes.
        """
    },

    "LDL": {
        "High": """
Your LDL cholesterol (the "bad" cholesterol) is elevated.

LDL is the type of cholesterol that builds up in your artery walls, forming plaques that can block blood flow and cause heart attacks or strokes.

**Optimal: Under 100 mg/dL**

**What to do:**
- Avoid trans fats (found in fried and processed foods)
- Eat soluble fiber — oats, apples, beans, and barley absorb LDL in your gut
- Eat fatty fish (salmon, sardines) twice a week
- Ask your doctor about statins if lifestyle changes don't help enough
        """
    },

    "HDL": {
        "Low": """
Your HDL cholesterol (the "good" cholesterol) is lower than ideal.

HDL actually helps remove LDL (bad cholesterol) from your arteries, so having more HDL is protective. Low HDL increases heart disease risk.

**What to do:**
- Exercise is one of the best ways to raise HDL — aim for 30 min of aerobic exercise daily
- Quit smoking if you smoke — smoking lowers HDL significantly
- Eat healthy fats: olive oil, avocado, nuts
- Avoid refined carbs and sugary foods
        """
    },

    "Triglycerides": {
        "High": """
Your triglycerides are elevated. Triglycerides are a type of fat in your blood.

Eating more calories than your body burns causes the excess to be stored as triglycerides.

**Normal: Under 150 mg/dL**
**Borderline: 150-199**
**High: 200-499**
**Very High: 500+**

**Main causes:**
- Eating too many sugary foods, refined carbs, alcohol
- Obesity or diabetes
- Hypothyroidism

**What to do:**
- Dramatically reduce sugar, alcohol, and white carbs
- Exercise regularly
- Eat more omega-3 fatty acids (fish, flaxseeds, walnuts)
        """
    },

    "Creatinine": {
        "High": """
Your creatinine level is elevated. Creatinine is a waste product that your kidneys filter out of your blood.

When creatinine is high, it usually means your kidneys are not filtering blood as well as they should.

**What this might mean:**
- Kidney disease or damage
- Dehydration (less water = kidneys work harder)
- High protein diet
- Certain medications

**What to do:**
- Drink more water — 2-3 litres per day
- Reduce protein intake (especially red meat and supplements)
- See a nephrologist (kidney specialist) — this is important
- Get a urine test and kidney function panel done
- Avoid NSAIDs like ibuprofen if possible
        """,
        "Critical": """
🚨 **Critically high creatinine.** Your kidneys may be in serious distress.

This requires immediate medical attention. Please go to a hospital or see a nephrologist today.
        """
    },

    "Uric Acid": {
        "High": """
Your uric acid level is elevated. This condition is called hyperuricemia.

High uric acid can crystallize in your joints, causing gout — which is very painful. It can also form kidney stones.

**What to do:**
- Drink plenty of water (at least 2-3 litres a day)
- Avoid high-purine foods: red meat, organ meats, shellfish, beer
- Reduce fructose (soft drinks and fruit juices)
- Cherries have been shown to reduce uric acid
- If you have gout symptoms (painful, swollen joints — often the big toe), see a doctor for medication
        """
    },

    "Bilirubin": {
        "High": """
Your bilirubin is elevated. Bilirubin is a yellow pigment produced when red blood cells break down. Your liver processes it.

High bilirubin can cause jaundice — yellow eyes and skin.

**What this might mean:**
- Liver conditions (hepatitis, fatty liver, cirrhosis)
- Bile duct blockage
- Excess breakdown of red blood cells
- Gilbert's syndrome (harmless genetic condition)

**What to do:**
- Get a full liver function test (LFT)
- Avoid alcohol completely
- See your doctor — the underlying cause needs to be identified
        """
    },

    "Vitamin D": {
        "Low": """
Your Vitamin D level is lower than normal. Vitamin D deficiency is extremely common in India (especially in cities) because we don't get enough sunlight.

**What Vitamin D does:**
- Strengthens bones and teeth
- Supports immune system
- Important for mood regulation

**Symptoms of deficiency:**
- Bone pain and muscle weakness
- Fatigue
- Mood changes, depression
- Frequent infections

**What to do:**
- Spend 15-20 minutes in morning sunlight daily
- Eat fatty fish, egg yolks, fortified milk
- Most importantly: take a Vitamin D3 supplement — your doctor will recommend the right dose based on your level
        """
    },

    "Vitamin B12": {
        "Low": """
Your Vitamin B12 is below normal. B12 deficiency is very common in vegetarians and vegans because B12 is mainly found in animal foods.

**What B12 deficiency causes:**
- Anemia (your blood can't carry oxygen properly)
- Nerve damage (numbness, tingling in hands and feet)
- Memory problems and brain fog
- Fatigue and weakness

**What to do:**
- If you're vegetarian/vegan, B12 supplementation is essential — there's no plant-based source
- Eat more eggs, dairy, meat, fish if you eat animal products
- B12 injections work faster than oral supplements for severe deficiency — talk to your doctor
        """
    },

    "SGPT": {
        "High": """
Your SGPT (also called ALT) is elevated. This is a liver enzyme, and high levels suggest liver inflammation or damage.

**Common causes:**
- Fatty liver disease (very common due to poor diet)
- Alcohol consumption
- Viral hepatitis (Hepatitis B or C)
- Certain medications
- Autoimmune conditions

**What to do:**
- Completely avoid alcohol
- Lose weight if overweight — even 5-10% weight loss helps fatty liver
- Avoid unnecessary medications and supplements
- Get an ultrasound of your liver
- See a gastroenterologist or hepatologist
        """
    },

    "HbA1c": {
        "High": """
Your HbA1c is elevated. This test shows your average blood sugar over the past 3 months.

**Interpretation:**
- Below 5.7% — Normal
- 5.7% - 6.4% — Pre-diabetes
- 6.5% and above — Diabetes

Unlike a regular glucose test which shows just that moment, HbA1c gives you the "big picture" of blood sugar control.

**What to do:**
- If above 6.5%, you should be formally diagnosed and treated for diabetes
- Strict diet control: no sugar, reduce refined carbs drastically
- Exercise daily — it's one of the most powerful ways to lower HbA1c
- Medication may be needed — see an endocrinologist or diabetologist
        """
    },

    "WBC": {
        "Low": """
Your white blood cell count is low (leukopenia). WBCs are your body's immune fighters.

**What this might mean:**
- Viral infections (the virus is using up your WBCs)
- Bone marrow problem
- Autoimmune disorder
- Side effect of some medications

**You might experience:**
- More frequent infections
- Infections that don't clear up quickly

**What to do:**
- See your doctor — this needs investigation
- Repeat the test to confirm (it can fluctuate)
        """,
        "High": """
Your white blood cell count is elevated (leukocytosis). WBCs go up when your body is fighting something.

**Common causes:**
- Active infection (bacterial or viral)
- Inflammation
- Physical or emotional stress
- Smoking
- Rarely, blood cancer (but this is uncommon)

**What to do:**
- Check if you have any infection symptoms
- See your doctor if it's very high or you feel unwell
- Repeat test after any infection clears up
        """
    },

    "Platelets": {
        "Low": """
Your platelet count is low (thrombocytopenia). Platelets are responsible for blood clotting.

**What this might mean:**
- Viral infections (dengue fever especially lowers platelets rapidly)
- Immune thrombocytopenia
- Liver disease
- Bone marrow problems
- Certain medications

**Warning signs — go to hospital immediately if you have:**
- Unusual bruising or purple spots on skin
- Bleeding from gums or nose that won't stop
- Blood in urine or stool

**What to do:**
- See your doctor urgently
- In dengue season, monitor platelet count daily if you had recent fever
        """,
        "High": """
Your platelet count is elevated. This is usually less concerning than low platelets.

**Common causes:**
- Iron deficiency anemia
- Infection or inflammation
- After surgery or trauma
- Rarely, a bone marrow condition

**What to do:**
- Usually no immediate action needed
- Let your doctor review in context of your full health picture
        """
    },

    "TSH": {
        "Low": """
Your TSH is lower than normal, which usually means your thyroid is overactive (hyperthyroidism).

**Symptoms you might have:**
- Weight loss despite eating normally
- Rapid or irregular heartbeat
- Anxiety and irritability
- Heat sensitivity and excessive sweating
- Trembling hands

**What to do:**
- See an endocrinologist
- Further thyroid tests needed: Free T3 and Free T4
        """,
        "High": """
Your TSH is higher than normal, which usually means your thyroid is underactive (hypothyroidism). This is extremely common, especially in women.

**Symptoms you might have:**
- Fatigue, feeling cold all the time
- Weight gain despite no change in diet
- Hair loss
- Depression and brain fog
- Constipation

**What to do:**
- See an endocrinologist or your GP
- Treatment is usually simple: a daily thyroid hormone tablet (levothyroxine)
- Most people feel much better once treatment starts
        """
    }
}


# --------------------------------------------------
# DIET RECOMMENDATIONS
# --------------------------------------------------
DIET_RECS = {
    "Hemoglobin": {
        "Low": {
            "include":   ["Spinach and leafy greens", "Lentils and dal", "Dates and raisins", "Red meat (in moderation)", "Kidney beans and chickpeas", "Tofu and tempeh", "Vitamin C rich foods (amla, oranges) — helps absorb iron"],
            "avoid":     ["Tea and coffee with meals — they block iron absorption", "Calcium-rich foods right before iron-rich meals"],
            "lifestyle": ["Cook in iron kadhai (cast iron vessels release iron into food)", "Take iron supplements only if prescribed", "Get re-tested after 3 months of supplementation"]
        }
    },
    "Glucose": {
        "High": {
            "include":   ["Bitter gourd (karela)", "Fenugreek seeds soaked overnight", "Whole grains (brown rice, millets, oats)", "Leafy vegetables", "Nuts and seeds", "Cinnamon tea"],
            "avoid":     ["Sugar, jaggery, honey", "White rice and maida products", "Fruit juices and cold drinks", "Processed snacks", "Alcohol"],
            "lifestyle": ["Walk 30-45 minutes every day", "Eat smaller meals more frequently", "Monitor blood sugar at home", "See a diabetologist if HbA1c is above 6.5%"]
        },
        "Low": {
            "include":   ["Complex carbs: oats, whole wheat, brown rice", "Frequent small meals every 3-4 hours", "Nuts and seeds as snacks", "Fruits"],
            "avoid":     ["Skipping meals", "Long gaps between eating"],
            "lifestyle": ["Always carry a quick sugar source like glucose biscuits or fruit", "Eat regular meals at consistent times"]
        }
    },
    "Cholesterol": {
        "High": {
            "include":   ["Oats (soluble fiber reduces LDL)", "Almonds and walnuts", "Fatty fish like salmon, sardines (omega-3)", "Olive oil instead of butter", "Garlic", "Avocado", "Green tea"],
            "avoid":     ["Fried foods of any kind", "Full-fat dairy products", "Red meat and processed meats", "Coconut oil and palm oil in excess", "Bakery items"],
            "lifestyle": ["45-minute walk or jog 5x per week", "Quit smoking — it dramatically raises heart disease risk", "Limit alcohol", "Reduce stress — cortisol raises cholesterol"]
        }
    },
    "LDL": {
        "High": {
            "include":   ["Soluble fiber: oats, apples, beans, barley", "Plant sterols (certain margarines, fortified foods)", "Fatty fish twice a week", "Walnuts and flaxseeds"],
            "avoid":     ["Trans fats in fried and packaged foods", "Saturated fats in butter, cream, red meat"],
            "lifestyle": ["Aerobic exercise 5x per week", "Maintain healthy body weight"]
        }
    },
    "Triglycerides": {
        "High": {
            "include":   ["Omega-3: fish, chia seeds, flaxseeds, walnuts", "Whole grains instead of refined carbs", "Vegetables", "Lean proteins"],
            "avoid":     ["Alcohol is the biggest culprit — avoid completely", "Sugar and sweets", "White bread, rice, maida", "Fruit juices (high in fructose)"],
            "lifestyle": ["Exercise daily", "Manage weight", "Control blood sugar if diabetic"]
        }
    },
    "Creatinine": {
        "High": {
            "include":   ["Plenty of water — at least 2-3 litres daily", "Fruits like apples and berries", "Cauliflower and cabbage", "Egg whites (low in phosphorus)"],
            "avoid":     ["High-protein foods — reduce red meat, chicken, protein powders", "High-sodium foods — no added salt, no papad/pickle", "NSAIDs like ibuprofen and aspirin", "Creatine supplements"],
            "lifestyle": ["See a nephrologist immediately", "Avoid strenuous exercise during this time", "Monitor blood pressure daily"]
        }
    },
    "Uric Acid": {
        "High": {
            "include":   ["Cherries — shown to reduce uric acid", "Lots of water (2-3 litres minimum)", "Vitamin C rich foods", "Low-fat dairy products", "Coffee (surprisingly protective)"],
            "avoid":     ["Red meat and organ meats (liver, kidney)", "Shellfish and certain fish (sardines, anchovies)", "Beer and alcohol", "Soft drinks with high fructose corn syrup"],
            "lifestyle": ["Lose weight gradually if overweight", "Avoid fasting or crash diets — they raise uric acid", "Exercise moderately"]
        }
    },
    "Vitamin D": {
        "Low": {
            "include":   ["Fatty fish: salmon, tuna, mackerel", "Egg yolks", "Fortified milk and cereals", "Mushrooms exposed to sunlight"],
            "avoid":     ["No specific foods to avoid"],
            "lifestyle": ["15-20 minutes of direct morning sunlight (before 10 AM) on skin daily", "Take Vitamin D3 + K2 supplement — dose depends on your level (ask your doctor)", "Re-test after 3 months of supplementation"]
        }
    },
    "Vitamin B12": {
        "Low": {
            "include":   ["Eggs, especially the yolk", "Dairy: milk, curd, paneer", "Fish and meat if non-vegetarian", "Fortified cereals and plant milk for vegans"],
            "avoid":     ["Excessive alcohol — it depletes B12"],
            "lifestyle": ["B12 supplements are essential for strict vegetarians/vegans — there's no reliable plant source", "Consider methylcobalamin form (better absorbed than cyanocobalamin)", "B12 injections may be recommended for severe deficiency"]
        }
    },
    "SGPT": {
        "High": {
            "include":   ["Green tea", "Turmeric (haldi) — has liver-protective properties", "Leafy greens and cruciferous vegetables", "Beetroot", "Coffee (2 cups/day has been shown to help fatty liver)"],
            "avoid":     ["Alcohol — completely avoid", "Processed and fried foods", "Excess sugar and fructose", "Unnecessary medications and supplements"],
            "lifestyle": ["Lose weight if overweight — the single most effective intervention", "Get a liver ultrasound", "See a gastroenterologist"]
        }
    },
    "HbA1c": {
        "High": {
            "include":   ["Same as high glucose", "Fenugreek seeds", "Bitter gourd regularly", "High-fiber vegetables"],
            "avoid":     ["Sugar in all forms", "Refined carbs", "Alcohol"],
            "lifestyle": ["Exercise is extremely effective — 30 min daily walking can reduce HbA1c significantly", "Strictly follow diabetic diet", "Monitor blood sugar at home", "Regular follow-ups with diabetologist"]
        }
    },
    "Bilirubin": {
        "High": {
            "include":   ["Plenty of water", "Fruits and vegetables", "Small, frequent, light meals"],
            "avoid":     ["Alcohol — completely avoid", "Fatty fried foods", "Raw shellfish", "Certain medications (ask your doctor)"],
            "lifestyle": ["Get a liver function test and ultrasound", "Rest adequately", "See a hepatologist or gastroenterologist"]
        }
    },
}


def get_explanation(parameter, value, status):
    """
    Returns a plain-language explanation for an abnormal test result.
    
    If we don't have a specific explanation, returns a generic message.
    """
    param_data = EXPLANATIONS.get(parameter)
    
    if not param_data:
        return f"""
Your {parameter} value is {value}. 

The reading shows: **{status}**

This value is outside the normal reference range. Please consult your doctor for a proper evaluation of this result and to understand what it means in the context of your overall health.
        """
    
    explanation = param_data.get(status)
    
    if not explanation:
        # Try High for anything that might be critical
        if status == "Critical":
            explanation = param_data.get("High") or param_data.get("Low") or ""
        if not explanation:
            return f"Your {parameter} is {status} (value: {value}). Please consult your doctor."
    
    return explanation.strip()


def get_diet_recommendations(parameter, status):
    """
    Returns diet and lifestyle recommendations for a given parameter + status.
    Returns None if we don't have recommendations for this combination.
    """
    param_data = DIET_RECS.get(parameter)
    if not param_data:
        return None
    return param_data.get(status)


def get_all_parameters():
    """Returns list of all parameters we have knowledge about"""
    return list(EXPLANATIONS.keys())
