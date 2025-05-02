import joblib
import pandas as pd
from django.core.exceptions import ObjectDoesNotExist
from .models import NFT 

def prep_data(nft):
    try:
        # Handle the materials field safely
        raw_materials = nft.product.materials
        if hasattr(raw_materials, 'all'):
            material_list = list(raw_materials.all())
        elif hasattr(raw_materials, '__iter__'):
            material_list = list(raw_materials)
        else:
            material_list = [raw_materials]

        data = {
            'root_category': nft.product.rootCategory.name,
            'main_category': nft.product.mainCategory.name,
            'materials': material_list,
            'condition': nft.product.condition,
            'recycled_content': nft.product.recycled_content,
            'recyclability': nft.product.recyclability,
            'carbon_footprint': nft.product.carbon_footprint,
            'energy_efficiency': nft.product.energy_efficiency,
            'durability': nft.product.durability,
            'repairability_score': nft.product.repairability_score,
            'ethical_sourcing': nft.product.ethical_sourcing,
            'cruelty_free': nft.product.cruelity_free,
            'plastic_free': nft.product.plastic_free,
            'natural': nft.product.natural,
            'destructable': nft.product.destructable,
            'hazardous': nft.product.hazardous,
        }

        df = pd.DataFrame([data])

        df['materials_str'] = df['materials'].apply(
            lambda x: ','.join([m.name for m in x]) if isinstance(x, (list, tuple)) else str(x.name)
        )
        df.drop(columns=['materials'], inplace=True)

        return df

    except AttributeError as e:
        print(f"[prep_data] Error: Invalid NFT data: {e}")
        raise ValueError(f"Invalid data in NFT object: {e}")

    except Exception as e:
        print(f"[prep_data] Unexpected error: {e}")
        raise

from decimal import Decimal

def calculate_reward(nftId):
    try:
        nft = NFT.objects.get(pk=nftId)
        score = Decimal(nft.product.sustainability_score)  # Convert float to Decimal
        owners = nft.total_owners
        
        base = (nft.price / Decimal("100")) * Decimal("10")
        reward = (base / Decimal("100") * score) * owners

        nft.reward = reward
        nft.save()

        print(f"[calculate_reward] Reward: {reward}")
        return reward
    except Exception as e:
        print(f"[calculate_reward] Error: {e}")
        raise e

        

def predict(pk):
    try:
        nft = NFT.objects.get(pk=pk)
        df = prep_data(nft)

        model_path = '/media/alastor/New Volume/EcoSwapChain/ESC-Backend/swap-server/ecoswapchain/esc_nft/gradient_boosting_model.pkl'
        model = joblib.load(model_path)

        predicted_score = model.predict(df)

        nft.product.sustainability_score = max(0, float(predicted_score[0]))
        nft.product.save()
        
        calculate_reward(nft.id)

        print(f"[predict] Predicted Sustainability Score: {predicted_score[0]}")

    except ObjectDoesNotExist as e:
        print(f"[predict] Error: NFT with pk {pk} not found.")
        raise e

    except FileNotFoundError as e:
        print("[predict] Error: Model file not found.")
        raise e

    except ValueError as ve:
        print(f"[predict] Data error: {ve}")
        raise ve

    except Exception as e:
        print(f"[predict] Unexpected error: {e}")
        raise e


