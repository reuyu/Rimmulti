using System;
using System.IO;
using System.Xml;
using System.Security.Cryptography;

class Program
{
    static readonly string ScratchDir = @"C:\Users\user\.gemini\antigravity-ide\brain\a0ee170e-bf70-46eb-a225-ec3b8fa3552c\scratch";
    static readonly string BaseTwoMapPath = @"C:\Users\user\Desktop\RimMulti\QA-Tactical-Engine\20261002\TwoMapFixtureV2.rws";
    static readonly string OutSavePath = Path.Combine(ScratchDir, @"OriginalSave\POC_TAC_ENGINE_02_MultiMap_Complex.rws");

    static void Main()
    {
        Console.WriteLine("================================================================");
        Console.WriteLine("Generating Complex Multi-Map Fixture: POC_TAC_ENGINE_02_MultiMap_Complex.rws");
        Console.WriteLine("Source: TwoMapFixtureV2.rws");
        Console.WriteLine("================================================================");

        var doc = new XmlDocument();
        doc.Load(BaseTwoMapPath);

        // 1. Locate Map 0 Things
        var map0Things = doc.SelectSingleNode("/savegame/game/maps/li[1]/things");
        if (map0Things == null) throw new InvalidOperationException("Map 0 things not found.");

        // 2. Configure Pawn Strange (Human302) on Map 0 with full complex graph
        var strange = doc.SelectSingleNode("/savegame/game/maps/li[1]/things/thing[id='Human302']");
        if (strange == null) throw new InvalidOperationException("Pawn Strange (Human302) not found on Map 0.");

        // (a) Equipped Weapon: Gun_Autopistol in equipment/equipment/innerList
        var eqInnerList = strange.SelectSingleNode("equipment/equipment/innerList");
        if (eqInnerList == null)
        {
            var eqContainer = strange.SelectSingleNode("equipment/equipment");
            if (eqContainer == null)
            {
                var eqRoot = strange.SelectSingleNode("equipment") ?? strange.AppendChild(doc.CreateElement("equipment"));
                eqContainer = eqRoot.AppendChild(doc.CreateElement("equipment"));
            }
            eqInnerList = eqContainer.AppendChild(doc.CreateElement("innerList"));
        }
        var wepFrag = doc.CreateDocumentFragment();
        wepFrag.InnerXml = @"<li Class=""ThingWithComps"">
            <def>Gun_Autopistol</def>
            <id>Gun_Autopistol9001</id>
            <health>100</health>
            <stackCount>1</stackCount>
            <questTags IsNull=""True"" />
            <despawnedTick>-1</despawnedTick>
            <verbTracker>
                <verbs>
                    <li Class=""Verb_Shoot"">
                        <loadID>CompEquippable_Gun_Autopistol9001_0</loadID>
                        <lastShotTick>-999999</lastShotTick>
                        <canHitNonTargetPawnsNow>True</canHitNonTargetPawnsNow>
                    </li>
                    <li Class=""Verb_MeleeAttackDamage"">
                        <loadID>CompEquippable_Gun_Autopistol9001_0_Smash</loadID>
                        <lastShotTick>-999999</lastShotTick>
                        <canHitNonTargetPawnsNow>True</canHitNonTargetPawnsNow>
                    </li>
                </verbs>
            </verbTracker>
        </li>";
        eqInnerList.AppendChild(wepFrag);

        // (b) Apparel: Add FlakVest to wornApparel/innerList
        var appInnerList = strange.SelectSingleNode("apparel/wornApparel/innerList");
        if (appInnerList != null)
        {
            var appFrag = doc.CreateDocumentFragment();
            appFrag.InnerXml = @"<li Class=""Apparel"">
                <def>Apparel_FlakVest</def>
                <id>Apparel_FlakVest9002</id>
                <health>200</health>
                <stackCount>1</stackCount>
                <stuff>Cloth</stuff>
                <questTags IsNull=""True"" />
                <despawnedTick>-1</despawnedTick>
                <quality>Good</quality>
                <sourcePrecept>null</sourcePrecept>
                <abilities />
            </li>";
            appInnerList.AppendChild(appFrag);
        }

        // (c) Inventory: Add MedicineIndustrial to inventory/innerContainer/innerList
        var invInnerList = strange.SelectSingleNode("inventory/innerContainer/innerList");
        if (invInnerList == null)
        {
            var invContainer = strange.SelectSingleNode("inventory/innerContainer");
            if (invContainer == null)
            {
                var invRoot = strange.SelectSingleNode("inventory") ?? strange.AppendChild(doc.CreateElement("inventory"));
                invContainer = invRoot.AppendChild(doc.CreateElement("innerContainer"));
            }
            invInnerList = invContainer.AppendChild(doc.CreateElement("innerList"));
        }
        var invFrag = doc.CreateDocumentFragment();
        invFrag.InnerXml = @"<li Class=""ThingWithComps"">
            <def>MedicineIndustrial</def>
            <id>MedicineIndustrial9004</id>
            <stackCount>5</stackCount>
            <health>100</health>
            <questTags IsNull=""True"" />
            <despawnedTick>-1</despawnedTick>
        </li>";
        invInnerList.AppendChild(invFrag);

        // (d) Health: Add BionicTongue (Hediff_AddedPart) to healthTracker/hediffSet/hediffs
        var hediffList = strange.SelectSingleNode("healthTracker/hediffSet/hediffs");
        if (hediffList != null)
        {
            var hediffFrag = doc.CreateDocumentFragment();
            hediffFrag.InnerXml = @"<li Class=""Hediff_AddedPart"">
                <ageTicks>1817</ageTicks>
                <visible>True</visible>
                <severity>0.5</severity>
                <canBeThreateningToPart>True</canBeThreateningToPart>
                <def>BionicTongue</def>
                <part>
                    <body>Human</body>
                    <index>22</index>
                </part>
                <combatLogEntry>null</combatLogEntry>
                <abilities IsNull=""True"" />
            </li>";
            hediffList.AppendChild(hediffFrag);
        }

        // (e) Bed Assignment
        var ownedBed = strange.SelectSingleNode("ownership/ownedBed");
        if (ownedBed != null)
        {
            ownedBed.InnerText = "Thing_Bed9104";
        }

        // 3. Add Player Settlement Buildings on Map 0
        string[] buildingsXml = new string[] {
            // Player Bed assigned to Strange
            @"<thing Class=""Building_Bed"">
                <def>Bed</def>
                <id>Bed9104</id>
                <map>0</map>
                <pos>(135, 0, 140)</pos>
                <rot>0</rot>
                <faction>Faction_10</faction>
                <stuff>WoodLog</stuff>
                <health>140</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <beenRevealed>True</beenRevealed>
                <assignedPawns>
                    <li>Thing_Human302</li>
                </assignedPawns>
                <uninstalledAssignedPawns />
                <alreadySetDefaultMed>True</alreadySetDefaultMed>
            </thing>",

            // Player Door
            @"<thing Class=""Building_Door"">
                <def>Door</def>
                <id>Door9103</id>
                <map>0</map>
                <pos>(135, 0, 138)</pos>
                <rot>0</rot>
                <faction>Faction_10</faction>
                <stuff>WoodLog</stuff>
                <health>150</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <beenRevealed>True</beenRevealed>
                <openInt>False</openInt>
                <holdOpenInt>False</holdOpenInt>
            </thing>",

            // Player Workbench
            @"<thing Class=""Building_WorkTable"">
                <def>TableSculpting</def>
                <id>TableSculpting9106</id>
                <map>0</map>
                <pos>(145, 0, 140)</pos>
                <rot>0</rot>
                <faction>Faction_10</faction>
                <stuff>WoodLog</stuff>
                <health>180</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <beenRevealed>True</beenRevealed>
                <billStack>
                    <bills />
                </billStack>
            </thing>",

            // Solar Generator
            @"<thing Class=""Building"">
                <def>SolarGenerator</def>
                <id>SolarGenerator9101</id>
                <map>0</map>
                <pos>(130, 0, 140)</pos>
                <rot>0</rot>
                <faction>Faction_10</faction>
                <health>300</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <beenRevealed>True</beenRevealed>
            </thing>",

            // Battery
            @"<thing Class=""Building_Battery"">
                <def>Battery</def>
                <id>Battery9102</id>
                <map>0</map>
                <pos>(133, 0, 140)</pos>
                <rot>0</rot>
                <faction>Faction_10</faction>
                <health>100</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <beenRevealed>True</beenRevealed>
                <storedEnergy>600</storedEnergy>
            </thing>",

            // Growing Rice Plant
            @"<thing Class=""Plant"">
                <def>Plant_Rice</def>
                <id>Plant_Rice9108</id>
                <map>0</map>
                <pos>(145, 0, 145)</pos>
                <health>85</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
                <growth>0.3500</growth>
                <age>5000</age>
            </thing>",

            // Tactical Proof Token (for manifest validation)
            @"<thing Class=""ThingWithComps"">
                <def>WarEconomy_TacticalProofToken</def>
                <id>WarEconomy_TacticalProofToken9109</id>
                <map>0</map>
                <pos>(140, 0, 144)</pos>
                <stackCount>10</stackCount>
                <health>100</health>
                <questTags IsNull=""True"" />
                <spawnedTick>0</spawnedTick>
                <despawnedTick>-1</despawnedTick>
            </thing>"
        };

        foreach (var bXml in buildingsXml)
        {
            var frag = doc.CreateDocumentFragment();
            frag.InnerXml = bXml;
            map0Things.AppendChild(frag);
        }

        // 4. Set Tamed Animal on Map 0 (Boomrat)
        var boomrat = doc.SelectSingleNode("/savegame/game/maps/li[1]/things/thing[id='Boomrat3383']");
        if (boomrat != null)
        {
            var factionNode = boomrat.SelectSingleNode("faction");
            if (factionNode != null) factionNode.InnerText = "Faction_10";
            var settingsFrag = doc.CreateDocumentFragment();
            settingsFrag.InnerXml = @"<playerSettings><joinMeditationArea IsNull=""True"" /><animalsRelease>False</animalsRelease><master>Thing_Human302</master><followDrafted>True</followDrafted><followFieldwork>True</followFieldwork></playerSettings>";
            boomrat.AppendChild(settingsFrag);
        }

        // 5. Add Stockpile Zone on Map 0
        var allZones = doc.SelectSingleNode("/savegame/game/maps/li[1]/zoneManager/allZones");
        if (allZones != null)
        {
            var zoneFrag = doc.CreateDocumentFragment();
            zoneFrag.InnerXml = @"<li Class=""Zone_Stockpile"">
                <ID>1</ID>
                <label>덤핑 저장구역 1</label>
                <cells>
                    <li>(140, 0, 140)</li>
                    <li>(141, 0, 140)</li>
                </cells>
                <settings>
                    <filter>
                        <allowedHitPointsPercents>0~1</allowedHitPointsPercents>
                    </filter>
                    <priorityInt>Important</priorityInt>
                </settings>
            </li>";
            allZones.AppendChild(zoneFrag);
        }

        // 6. Save document
        Directory.CreateDirectory(Path.GetDirectoryName(OutSavePath)!);
        doc.Save(OutSavePath);

        long size = new FileInfo(OutSavePath).Length;
        string hash = "";
        using (var sha = SHA256.Create())
        using (var fs = File.OpenRead(OutSavePath))
        {
            hash = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "");
        }

        Console.WriteLine($"[Success] Created fixture at: {OutSavePath}");
        Console.WriteLine($"Size: {size:N0} bytes");
        Console.WriteLine($"SHA256: {hash}");
    }
}
