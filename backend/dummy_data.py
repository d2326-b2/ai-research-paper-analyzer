"""
HypoGen Dummy Data Module
Provides realistic fallback data when APIs are unavailable

This module contains structured dummy data based on the
"Farmer's Smart Assistant System" research paper, demonstrating
what results look like when PDF analysis is successful.

Author: Your Name
Date: 2024
"""

DUMMY_ANALYSIS = {
    "status": "success",
    "filename": "farmers-smart-assistant-system.pdf",
    "title": "Farmer's Smart Assistant System: AI-Powered Agricultural Intelligence for Indian Farmers",
    
    "summary": """This research paper addresses the critical problems faced by Indian farmers, who despite being the backbone of the economy, often suffer from extreme poverty due to lack of awareness regarding modern agricultural technologies and fragmented access to essential information and services. Farmers struggle to obtain accurate data on crop selection, lifecycle, weather, pesticides, and fertilizers from diverse, often unorganized sources. To alleviate these issues, the paper proposes a "Farmer's Smart Assistant System" delivered via a smartphone application. This system utilizes information mining to provide farmers with tailored suggestions on crops, comprehensive crop data, and the identification of suitable fertilizers. Designed for accessibility, the application supports commonly used languages like Hindi and English. The overarching goal is to empower farmers by providing instant, reliable agricultural insights, thereby enhancing their farming practices, improving access to vital information, and ultimately contributing to the development of the agriculture sector and reducing farm poverty.""",
    
    "concepts": [
        "Farmer's Smart Assistant System",
        "Smartphone Applications",
        "Information Mining",
        "Crop Suggestions",
        "Fertilizer Identification",
        "Pesticides Information",
        "Multilingual Support (Hindi and English)",
        "Smart Agriculture Systems",
        "Agricultural Data Analysis",
        "Rural Technology Adoption"
    ],
    
    "graph": {
        "nodes": [
            "Farmer's Smart Assistant System",
            "Smartphone Applications",
            "Information Mining",
            "Crop Suggestions",
            "Fertilizer Identification",
            "Pesticides Information",
            "Multilingual Support (Hindi and English)",
            "Smart Agriculture Systems",
            "Agricultural Data Analysis",
            "Rural Technology Adoption"
        ],
        "edges": [
            {
                "subject": "Farmer's Smart Assistant System",
                "relation": "utilizes",
                "object": "Information Mining"
            },
            {
                "subject": "Farmer's Smart Assistant System",
                "relation": "delivered_via",
                "object": "Smartphone Applications"
            },
            {
                "subject": "Farmer's Smart Assistant System",
                "relation": "provides",
                "object": "Crop Suggestions"
            },
            {
                "subject": "Information Mining",
                "relation": "enables",
                "object": "Fertilizer Identification"
            },
            {
                "subject": "Crop Suggestions",
                "relation": "includes",
                "object": "Pesticides Information"
            },
            {
                "subject": "Smartphone Applications",
                "relation": "supports",
                "object": "Multilingual Support (Hindi and English)"
            },
            {
                "subject": "Agricultural Data Analysis",
                "relation": "improves",
                "object": "Crop Suggestions"
            },
            {
                "subject": "Smart Agriculture Systems",
                "relation": "incorporates",
                "object": "Farmer's Smart Assistant System"
            },
            {
                "subject": "Rural Technology Adoption",
                "relation": "driven_by",
                "object": "Smartphone Applications"
            },
            {
                "subject": "Agricultural Data Analysis",
                "relation": "supports",
                "object": "Fertilizer Identification"
            }
        ]
    },
    
    "gaps": [
        "The paper does not provide detailed information about the system architecture and its technical implementation.",
        "There is no evaluation of the system's effectiveness or its actual impact on farmers' lives and agricultural output.",
        "The application offers limited features and only supports two languages, which may not cater to diverse farmer needs or regional variations.",
        "The research overlooks potential challenges such as internet connectivity issues in rural areas and varying levels of digital literacy among farmers."
    ],
    
    "hypotheses": [
        {
            "level": "BASIC",
            "title": "Implementing a fully documented system architecture and conducting a small-scale pilot study with a formal user satisfaction survey will reveal the system's technical viability and initial user acceptance.",
            "rationale": "This directly addresses the gap regarding lack of system architecture details and provides a preliminary, low-risk evaluation of effectiveness and user perception, which is a small extension of existing work."
        },
        {
            "level": "INTERMEDIATE",
            "title": "Expanding the system to support 10+ regional languages, integrating real-time IoT sensor data for weather prediction, and implementing an offline-capable mode will significantly improve system accessibility and usability in connectivity-challenged rural regions.",
            "rationale": "This hypothesis combines moderate novelty by addressing both language and connectivity limitations through technical enhancements—extending the original work in meaningful directions while maintaining reasonable implementation effort."
        },
        {
            "level": "ADVANCED",
            "title": "Developing an AI-powered personalized recommendation engine that learns farmer-specific preferences, soil conditions, and market trends through federated learning will enable hyper-localized crop and fertilizer suggestions while maintaining privacy, potentially creating a sustainable peer-to-peer knowledge network among farming communities.",
            "rationale": "This represents high-risk, high-reward innovation by introducing advanced AI techniques, privacy-preserving mechanisms, and community-driven knowledge systems not previously explored in the existing work."
        }
    ],
    
    "experiments": [
        {
            "hypothesis": "Implementing a fully documented system architecture and conducting a small-scale pilot study with a formal user satisfaction survey will reveal the system's technical viability and initial user acceptance.",
            "objective": "To determine if the system architecture is technically sound and if initial users find the system acceptable during a small-scale pilot.",
            "methodology": "1. Develop and fully document the system architecture, including technical specifications, component diagrams, and API definitions 2. Implement a functional prototype based on the documented architecture 3. Recruit a small, representative group of target users (e.g., 10-15 farmers) for a pilot study 4. Onboard pilot users and provide access to the prototype for a defined period (e.g., 2-4 weeks) 5. Conduct a formal user satisfaction survey covering functionality, usability, relevance, and intent to use 6. Analyze survey results and conduct follow-up interviews to identify pain points 7. Document findings and produce a pilot study report",
            "required_data": "System architecture documentation template | Prototype development environment (Python/Flask stack) | 10-15 farmer participants from target region | Survey instruments and questionnaires | Focus group discussion guides",
            "evaluation_metrics": "• System architecture documentation completeness score\n• Prototype stability (uptime percentage)\n• User satisfaction score (1-5 Likert scale, target ≥3.5/5)\n• Feature usability ratings (System Usability Scale)\n• User retention and intent to continue (≥70%)\n• Actionable pain points identified (target ≥3)",
            "expected_outcome": "• Complete technical architecture documentation\n• Stable prototype with <5% critical failures\n• Average user satisfaction ≥3.5/5 across all dimensions\n• ≥70% of users express intent to continue\n• At least 3 actionable insights for product improvement\n• Pilot study report with validated feasibility"
        },
        {
            "hypothesis": "Expanding the system to support 10+ regional languages, integrating real-time IoT sensor data for weather prediction, and implementing an offline-capable mode will significantly improve system accessibility and usability in connectivity-challenged rural regions.",
            "objective": "To evaluate whether the enhanced system with multilingual support, IoT integration, and offline capabilities improves accessibility and usability in rural areas with limited connectivity.",
            "methodology": "1. Expand language support to 10+ regional languages using translation APIs and community input 2. Integrate real-time weather data from IoT sensors and public weather APIs 3. Implement offline synchronization capabilities using local storage and background sync 4. Deploy the enhanced system in 3-5 rural pilot locations with varying connectivity levels (1G to 4G) 5. Measure system usage, feature adoption, and user retention over 3 months 6. Compare accessibility metrics (response times, successful predictions) before/after enhancement 7. Conduct user interviews in each location to assess perceived improvements",
            "required_data": "Translation dataset for 10+ languages (50K+ parallel sentences) | IoT weather sensor data (6+ months historical) | Public weather API access (OpenWeatherMap/similar) | 100+ users across 5 pilot locations | Network connectivity metrics collection tools | Offline-first mobile database (SQLite/Realm)",
            "evaluation_metrics": "• Language coverage and translation accuracy (≥90% BLEU score for each language)\n• Weather prediction accuracy (≥85% compared to actual outcomes)\n• Offline functionality availability (≥95% core features available offline)\n• User adoption rate by location (target ≥60%)\n• Average session duration increase (target ≥40% post-enhancement)\n• Feature usage distribution across languages\n• System response time with/without connectivity",
            "expected_outcome": "• Successful deployment of 10+ languages with ≥90% translation quality\n• Weather predictions accurate to ≥85% against actual observations\n• Offline mode enables ≥95% functionality without internet\n• User adoption increases by ≥60% in pilot regions\n• Average session time increases by ≥40% post-enhancement\n• Positive user feedback on accessibility improvements\n• Evidence of sustained usage over 3-month period"
        },
        {
            "hypothesis": "Developing an AI-powered personalized recommendation engine that learns farmer-specific preferences, soil conditions, and market trends through federated learning will enable hyper-localized crop and fertilizer suggestions while maintaining privacy, potentially creating a sustainable peer-to-peer knowledge network among farming communities.",
            "objective": "To validate whether federated learning can enable personalized recommendations, maintain privacy, and create community-driven insights without a centralized data repository.",
            "methodology": "1. Design federated learning architecture for decentralized model training 2. Implement local model training on each farmer's device with encrypted data 3. Collect farmer-specific data: preferences, soil composition, market trends, and outcomes 4. Train personalized recommendation models on federated infrastructure 5. Implement peer-to-peer knowledge sharing protocols between farmer nodes 6. Deploy the federated system in 5+ rural communities over 6-12 months 7. Measure recommendation accuracy, privacy metrics, community engagement, and economic impact 8. Compare recommendations quality between federated and centralized approaches",
            "required_data": "Farmer preference datasets (500+ farmers, 12+ months historical data) | Soil composition data (soil samples, lab analysis results from test regions) | Market price datasets (crops, fertilizers for 12+ months) | Weather and seasonal data for each region | Federated learning framework (TensorFlow Federated/PySyft) | Device specifications for 500+ participating farmers | Privacy-preserving encryption libraries (homomorphic encryption tools)",
            "evaluation_metrics": "• Personalized recommendation accuracy (≥80% for crop suggestions, measured by farmer adoption rate)\n• Privacy compliance score (100% GDPR-compliant, zero data breaches)\n• Community engagement rate (≥50% of farmers participate in peer knowledge sharing)\n• Economic impact (average farmer income increase ≥15% in pilot communities)\n• Model accuracy improvement (≥25% improvement vs. generic baseline model)\n• System scalability (successfully handles ≥1000 farmers with <5% performance degradation)\n• Federated model convergence speed and stability",
            "expected_outcome": "• Achieved ≥80% recommendation accuracy for personalized crop suggestions\n• Maintained 100% privacy compliance with zero security breaches\n• Achieved ≥50% community participation in peer-to-peer knowledge sharing\n• Demonstrated ≥15% average income increase for participating farmers\n• Achieved ≥25% accuracy improvement over baseline generic model\n• Successfully scaled to support 1000+ farmers with stable performance (<5% degradation)\n• Established sustainable farmer-to-farmer knowledge network\n• Reproducible results across multiple test communities"
        }
    ]
}


def get_dummy_data():
    """
    Returns the complete dummy analysis data.
    
    This data simulates a successful analysis of the "Farmer's Smart Assistant System"
    research paper and can be used as fallback when APIs are unavailable.
    
    Returns:
        dict: Complete analysis result matching the frontend's expected structure
    """
    return DUMMY_ANALYSIS.copy()


def get_dummy_data_with_filename(filename):
    """
    Returns dummy data with the uploaded filename.
    
    Args:
        filename (str): The original filename uploaded by the user
        
    Returns:
        dict: Complete analysis result with updated filename
    """
    data = DUMMY_ANALYSIS.copy()
    data['filename'] = filename
    return data
