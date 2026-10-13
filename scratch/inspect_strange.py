with open('scratch/Profiles/Profile_Neg3_SavedBytes/Saves/Staging_Stage_Shoot_20261004_071608880.rws', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Strange')
ht_before = text.rfind('<healthTracker>', 0, idx)
print("Hediff excerpt before Strange:")
print(text[ht_before:ht_before+800])

inv_before = text.rfind('<inventory>', 0, idx)
print("\nInventory excerpt before Strange:")
print(text[inv_before:inv_before+800])
