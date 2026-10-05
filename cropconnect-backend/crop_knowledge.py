"""Static agronomic requirements used by the crop suitability engine.

The pH ranges follow Indian agricultural-extension guidance (including TNAU
crop-tolerance tables). Temperature, relative humidity, and root-zone moisture
ranges are practical growing ranges for the crops, not sensor calibration
thresholds. Nutrient ranges are deliberately ``None``: an N/P/K mg/kg result
depends on the laboratory extraction method, so it must not be compared with a
generic number.

``rainfall_range`` is an indicative 7-day rainfall band in millimetres,
derived from typical weekly water need during the crop's active growth stage
(not the full-season total). It is intentionally coarse: it exists to give
the suitability engine a usable signal for the paper's weather input (Xw),
not to serve as a precise irrigation-scheduling figure. Treat it the same way
as the nutrient ranges — an approximation to be refined once real field data
is available, not a validated agronomic constant.
"""

from typing import Any


def _crop(
    name: str, category: str, season: str, crop_type: str, ph_range: list[float],
    moisture_range: list[float], temp_range: list[float], humidity_range: list[float],
    rainfall_range: list[float], suitable_regions: list[str], description: str,
) -> dict[str, Any]:
    return {
        "name": name,
        "category": category,
        "season": season,
        "crop_type": crop_type,
        "ph_range": ph_range,
        "moisture_range": moisture_range,
        "temp_range": temp_range,
        "humidity_range": humidity_range,
        "rainfall_range": rainfall_range,
        "nitrogen_range": None,
        "phosphorus_range": None,
        "potassium_range": None,
        "suitable_regions": suitable_regions,
        "description_template": description,
    }


CROP_DATABASE: list[dict[str, Any]] = [
    _crop("Rice", "Cereal", "Kharif", "Food Crops", [5.0, 6.5], [60, 90], [20, 35], [70, 90], [40, 100], ["West Bengal", "Uttar Pradesh", "Punjab", "Odisha", "Andhra Pradesh", "Tamil Nadu"], "Rice is a warm-season cereal that performs best with consistently wet soil."),
    _crop("Wheat", "Cereal", "Rabi", "Food Crops", [6.0, 7.5], [35, 60], [10, 25], [40, 65], [10, 35], ["Uttar Pradesh", "Punjab", "Haryana", "Madhya Pradesh", "Rajasthan"], "Wheat is a cool-season cereal suited to moderately moist, well-drained soil."),
    _crop("Soybean", "Oilseed", "Kharif", "Food Crops", [5.5, 7.0], [40, 65], [20, 30], [55, 75], [25, 60], ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Karnataka"], "Soybean is a monsoon oilseed that needs warm conditions and good drainage."),
    _crop("Maize", "Cereal", "Kharif", "Food Crops", [6.0, 7.5], [40, 65], [18, 32], [50, 75], [20, 55], ["Karnataka", "Madhya Pradesh", "Bihar", "Telangana", "Rajasthan"], "Maize is a warm-season cereal that grows well in fertile, well-drained soil."),
    _crop("Cotton", "Fibre", "Kharif", "Cash Crops", [5.5, 7.5], [35, 60], [21, 35], [45, 65], [15, 45], ["Gujarat", "Maharashtra", "Telangana", "Punjab", "Haryana"], "Cotton is a warm-season fibre crop that needs a long frost-free growing period."),
    _crop("Groundnut", "Oilseed", "Kharif", "Food Crops", [5.3, 6.6], [30, 55], [20, 30], [50, 70], [15, 40], ["Gujarat", "Rajasthan", "Tamil Nadu", "Andhra Pradesh", "Karnataka"], "Groundnut is an oilseed crop that prefers warm, loose, well-drained soil."),
    _crop("Sugarcane", "Sugar crop", "Perennial", "Cash Crops", [6.0, 7.5], [55, 80], [20, 35], [60, 85], [30, 90], ["Uttar Pradesh", "Maharashtra", "Karnataka", "Tamil Nadu", "Bihar"], "Sugarcane is a long-duration tropical crop with a high and regular water need."),
    _crop("Chickpea", "Pulse", "Rabi", "Food Crops", [6.0, 8.0], [25, 45], [15, 25], [35, 55], [0, 20], ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Karnataka"], "Chickpea is a cool-season pulse that prefers relatively dry, well-drained conditions."),
    _crop("Mustard", "Oilseed", "Rabi", "Food Crops", [6.0, 7.5], [25, 45], [10, 25], [35, 60], [0, 25], ["Rajasthan", "Uttar Pradesh", "Haryana", "Madhya Pradesh", "West Bengal"], "Mustard is a cool-season oilseed crop that does best without prolonged waterlogging."),
    _crop("Bajra", "Millet", "Kharif", "Food Crops", [5.0, 6.5], [20, 45], [25, 35], [35, 60], [10, 35], ["Rajasthan", "Maharashtra", "Gujarat", "Haryana", "Uttar Pradesh"], "Bajra is a drought-tolerant millet suitable for warm, comparatively dry fields."),
    _crop("Jowar", "Millet", "Kharif", "Food Crops", [6.0, 7.5], [25, 50], [25, 35], [40, 65], [15, 40], ["Maharashtra", "Karnataka", "Madhya Pradesh", "Telangana", "Rajasthan"], "Jowar is a hardy warm-season millet that tolerates lower soil moisture than rice or sugarcane."),
    _crop("Tomato", "Vegetable", "Zaid", "Horticulture Crops", [6.0, 7.0], [45, 70], [18, 30], [50, 70], [15, 45], ["Maharashtra", "Karnataka", "Andhra Pradesh", "Madhya Pradesh", "West Bengal"], "Tomato is a warm-season vegetable that needs even moisture and well-drained soil."),
    _crop("Onion", "Vegetable", "Rabi", "Horticulture Crops", [6.0, 7.0], [35, 60], [13, 28], [50, 70], [5, 30], ["Maharashtra", "Madhya Pradesh", "Karnataka", "Gujarat", "Rajasthan"], "Onion is a cool-to-mild season vegetable that prefers loose, well-drained soil."),
    _crop("Potato", "Tuber", "Rabi", "Horticulture Crops", [5.0, 6.5], [45, 70], [15, 25], [60, 80], [10, 35], ["Uttar Pradesh", "West Bengal", "Bihar", "Punjab", "Gujarat"], "Potato is a cool-season tuber crop that benefits from steady moisture without waterlogging."),
    _crop("Sunflower", "Oilseed", "Zaid", "Food Crops", [6.0, 7.5], [30, 55], [20, 30], [40, 65], [10, 35], ["Karnataka", "Maharashtra", "Andhra Pradesh", "Telangana", "Tamil Nadu"], "Sunflower is a warm-season oilseed that performs well in well-drained soil."),
    # The following entries extend coverage to match the 22-crop label set
    # used by the trained ML model (scripts/train_crop_model.py), so the
    # rule-based fallback engine can recommend from the same crop universe
    # the ML path can, rather than silently narrowing the farmer's options
    # whenever the model is unavailable. Ranges are indicative estimates in
    # the same spirit as the crops above -- not lab-validated constants.
    _crop("Apple", "Fruit", "Perennial", "Horticulture Crops", [5.5, 6.5], [40, 60], [15, 24], [50, 70], [15, 40], ["Himachal Pradesh", "Jammu and Kashmir", "Uttarakhand"], "Apple is a temperate fruit tree that needs cool growing conditions and well-drained soil."),
    _crop("Banana", "Fruit", "Perennial", "Horticulture Crops", [5.5, 7.0], [60, 85], [22, 32], [65, 85], [40, 90], ["Tamil Nadu", "Maharashtra", "Gujarat", "Andhra Pradesh", "Karnataka"], "Banana is a tropical fruit crop with a consistently high water requirement."),
    _crop("Blackgram", "Pulse", "Kharif", "Food Crops", [6.0, 7.5], [30, 55], [25, 35], [40, 65], [15, 45], ["Madhya Pradesh", "Maharashtra", "Rajasthan", "Uttar Pradesh", "Andhra Pradesh"], "Blackgram (urad) is a warm-season pulse that tolerates moderate moisture stress."),
    _crop("Coconut", "Plantation crop", "Perennial", "Horticulture Crops", [5.5, 7.5], [55, 80], [25, 32], [70, 90], [30, 70], ["Kerala", "Tamil Nadu", "Karnataka", "Andhra Pradesh"], "Coconut is a coastal tropical palm that favours consistently humid, well-drained conditions."),
    _crop("Coffee", "Plantation crop", "Perennial", "Horticulture Crops", [5.0, 6.5], [50, 70], [15, 28], [60, 80], [30, 70], ["Karnataka", "Kerala", "Tamil Nadu"], "Coffee is a shade-grown perennial crop that prefers cool, humid hill conditions."),
    _crop("Grapes", "Fruit", "Rabi", "Horticulture Crops", [6.0, 7.5], [35, 60], [15, 35], [40, 65], [5, 25], ["Maharashtra", "Karnataka", "Tamil Nadu"], "Grapes are a warm-season fruit crop that generally prefers drier conditions with controlled irrigation."),
    _crop("Jute", "Fibre", "Kharif", "Cash Crops", [6.0, 7.5], [55, 80], [24, 37], [65, 90], [40, 90], ["West Bengal", "Bihar", "Assam", "Odisha"], "Jute is a warm-season fibre crop that needs consistently high moisture and humidity."),
    _crop("Kidneybeans", "Pulse", "Kharif", "Food Crops", [5.5, 7.0], [35, 60], [15, 27], [40, 65], [15, 45], ["Himachal Pradesh", "Uttarakhand", "Jammu and Kashmir"], "Kidney beans (rajma) are a cool-to-mild season pulse suited to hill agriculture."),
    _crop("Lentil", "Pulse", "Rabi", "Food Crops", [6.0, 7.5], [25, 45], [15, 25], [35, 55], [0, 20], ["Madhya Pradesh", "Uttar Pradesh", "Bihar", "West Bengal"], "Lentil (masoor) is a cool-season pulse that prefers relatively dry, well-drained soil."),
    _crop("Mango", "Fruit", "Perennial", "Horticulture Crops", [5.5, 7.5], [40, 65], [24, 35], [50, 75], [15, 45], ["Uttar Pradesh", "Andhra Pradesh", "Karnataka", "Bihar", "Gujarat"], "Mango is a tropical fruit tree that tolerates moderate moisture variation once established."),
    _crop("Mothbeans", "Pulse", "Kharif", "Food Crops", [6.0, 7.5], [15, 40], [25, 37], [30, 55], [5, 25], ["Rajasthan", "Gujarat", "Haryana"], "Moth beans are a highly drought-tolerant pulse suited to arid and semi-arid conditions."),
    _crop("Mungbean", "Pulse", "Kharif", "Food Crops", [6.0, 7.5], [30, 55], [25, 35], [45, 70], [15, 45], ["Rajasthan", "Maharashtra", "Andhra Pradesh", "Karnataka", "Madhya Pradesh"], "Mungbean (green gram) is a short-duration warm-season pulse."),
    _crop("Muskmelon", "Fruit", "Zaid", "Horticulture Crops", [6.0, 7.0], [40, 65], [24, 35], [45, 70], [10, 35], ["Uttar Pradesh", "Punjab", "Haryana", "Maharashtra"], "Muskmelon is a warm-season fruit crop grown mainly in the dry summer season with irrigation."),
    _crop("Orange", "Fruit", "Perennial", "Horticulture Crops", [5.5, 7.0], [40, 65], [15, 30], [50, 75], [15, 45], ["Maharashtra", "Madhya Pradesh", "Andhra Pradesh"], "Orange is a citrus fruit tree that prefers well-drained soil and moderate humidity."),
    _crop("Papaya", "Fruit", "Perennial", "Horticulture Crops", [6.0, 7.0], [50, 75], [22, 32], [60, 85], [25, 60], ["Andhra Pradesh", "Karnataka", "Gujarat", "Madhya Pradesh"], "Papaya is a fast-growing tropical fruit crop that needs consistent moisture without waterlogging."),
    _crop("Pigeonpeas", "Pulse", "Kharif", "Food Crops", [6.0, 7.5], [30, 55], [22, 32], [40, 65], [15, 45], ["Maharashtra", "Karnataka", "Madhya Pradesh", "Uttar Pradesh"], "Pigeon pea (tur/arhar) is a warm-season pulse with a relatively long growing period."),
    _crop("Pomegranate", "Fruit", "Perennial", "Horticulture Crops", [6.0, 7.5], [30, 55], [20, 35], [35, 60], [5, 25], ["Maharashtra", "Karnataka", "Gujarat", "Andhra Pradesh"], "Pomegranate is a drought-tolerant fruit crop that prefers drier conditions with controlled irrigation."),
    _crop("Watermelon", "Fruit", "Zaid", "Horticulture Crops", [6.0, 7.0], [45, 70], [24, 35], [45, 70], [10, 35], ["Uttar Pradesh", "Madhya Pradesh", "Andhra Pradesh", "West Bengal"], "Watermelon is a warm-season fruit crop typically grown in the dry season with irrigation."),
]
