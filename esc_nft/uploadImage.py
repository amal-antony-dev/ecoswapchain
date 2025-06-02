import os
import json
import requests
from decouple import RepositoryEnv, Config
from ecoswapchain.settings import pinata_jwt


def pin_file_to_ipfs(file_path):
    """Uploads an image to IPFS via Pinata."""
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            headers = {"Authorization": f"Bearer {pinata_jwt}"}

            response = requests.post(url, files=files, headers=headers)
            response.raise_for_status()  # Raise HTTP errors

            cid = response.json().get("IpfsHash")
            if not cid:
                print("❌ No CID returned from Pinata.")
                return None

            print(f"✅ Image uploaded successfully! CID: {cid}")
            print(f"🔗 View the image at: https://gateway.pinata.cloud/ipfs/{cid}")
            return cid

    except requests.exceptions.RequestException as e:
        print(f"❌ Error uploading image: {e}")
        return None
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None


def pin_metadata_to_ipfs(image_cid, nft):
    """Uploads metadata to IPFS via Pinata."""
    if not image_cid:
        print("❌ Image CID is missing. Metadata upload aborted.")
        return None

    url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
    try:
        metadata = {
        "name": nft.name,
        "symbol": nft.symbol,
        "description": nft.description,
        "image": f"https://gateway.pinata.cloud/ipfs/{image_cid}",
        "ownerAddress": getattr(nft.owner.eco_user, "email", "Unknown"),
        "attributes": [
        {"trait_type": "Category", "value": getattr(nft.product.rootCategory, "name", "Unknown") if nft.product else "Unknown"},
        {"trait_type": "Subcategory", "value": getattr(nft.product.mainCategory, "name", "Unknown") if nft.product else "Unknown"},
        {"trait_type": "Condition", "value": getattr(nft.product, "condition", "Not specified")},
        {"trait_type": "Recycled Content (%)", "value": getattr(nft.product, "recycled_content", 0.0)},
        {"trait_type": "Recyclability", "value": "Yes" if getattr(nft.product, "recyclability", False) else "No"},
        {"trait_type": "Carbon Footprint (kg CO2e)", "value": getattr(nft.product, "carbon_footprint", 0.0)},
        {"trait_type": "Energy Efficiency (kWh/year)", "value": getattr(nft.product, "energy_efficiency", 0.0)},
        {"trait_type": "Durability (years)", "value": getattr(nft.product, "durability", 0)},
        {"trait_type": "Repairability Score (0-100)", "value": getattr(nft.product, "repairability_score", 0.0)},
        {"trait_type": "Ethical Sourcing", "value": "Yes" if getattr(nft.product, "ethical_sourcing", False) else "No"},
        {"trait_type": "Cruelty-Free", "value": "Yes" if getattr(nft.product, "cruelty_free", False) else "No"},
        {"trait_type": "Plastic-Free", "value": "Yes" if getattr(nft.product, "plastic_free", False) else "No"},
        {"trait_type": "Natural Materials", "value": "Yes" if getattr(nft.product, "natural", False) else "No"},
        {"trait_type": "Destructible", "value": "Yes" if getattr(nft.product, "destructable", False) else "No"},
        {"trait_type": "Hazardous", "value": "Yes" if getattr(nft.product, "hazardous", False) else "No"},
        {"trait_type": "Exchangeable", "value": "Yes" if getattr(nft, "exchange", False) else "No"},
        {"trait_type": "Owner", "value": getattr(nft.owner.wallet, "public_key", "Unknown")},
    ],
    "price": float(nft.price) if nft.price else 0.0
        
}


        headers = {
            "Authorization": f"Bearer {env_config.get('PINATA_JWT')}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, json=metadata)
        response.raise_for_status()

        metadata_cid = response.json().get("IpfsHash")
        if not metadata_cid:
            print("❌ No metadata CID returned from Pinata.")
            return None

        print(f"✅ Metadata uploaded successfully! CID: {metadata_cid}")
        print(f"🔗 View metadata at: https://gateway.pinata.cloud/ipfs/{metadata_cid}")
        return metadata_cid

    except requests.exceptions.RequestException as e:
        print(f"❌ Error uploading metadata: {e}")
        return None


def get_uri(nft):
    """Uploads the NFT's image and metadata to IPFS and returns the metadata URI."""
    try:
        image_cid = pin_file_to_ipfs(nft.mainImage.path)  # Ensure `mainImage` is a FileField or path
        if not image_cid:
            return None  # Handle image upload failure

        metadata_cid = pin_metadata_to_ipfs(image_cid, nft)
        if not metadata_cid:
            return None  # Handle metadata upload failure

        return {"uri": f"https://gateway.pinata.cloud/ipfs/{metadata_cid}"}

    except AttributeError as e:
        print(f"❌ Error accessing NFT attributes: {e}")
        return None
