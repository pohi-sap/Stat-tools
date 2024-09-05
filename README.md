# Stat-tools
- **tx_statutes.py** - This is a Python CLI Tool for getting text of a Texas Statute.

## Planned features: 

- [ ] json output [requested](https://github.com/pohi-sap/Stat-tools/issues/1)

## Get Help with this CLI tool or just look around 😊
```bash
python3 tx_statutes.py -h
```


# Quick start
This tool will get you all the text from a texas statute, you only need to specify [source](#sources) and statute info.

Texas statutes are searchable [here](https://statutes.capitol.texas.gov/Index.aspx)

## Sources
Statute Sources are specified using two letters, case insensitive.
To get a current list of some, use:
```bash
python3 tx_statutes.py --list-sources
```

## Basic useage
By default, this thing will try and use a cache folder.
For example when you do this:
```bash
python3 tx_statutes.py --source tx --statute 11.1827
```
It will prompt with the following:
```bash
Existing statute cache folder not found
Do you want to create it now? ~38MB [Y/n]
```
If you type in `Y`, statute zip folders will be downloaded from 'https://statutes.capitol.texas.gov/Download.aspx' to ./statute_cache
```text
Creating cache, then continuing with searching for statute.
Downloaded file ./statute_cache/CN.htm.zip
Downloaded file ./statute_cache/BO.htm.zip
Downloaded file ./statute_cache/I1.htm.zip
Downloaded file ./statute_cache/AL.htm.zip
Downloaded file ./statute_cache/HR.htm.zip
Downloaded file ./statute_cache/AL.htm.zip
Downloaded file ./statute_cache/AG.htm.zip
Downloaded file ./statute_cache/FA.htm.zip
Downloaded file ./statute_cache/EL.htm.zip
Downloaded file ./statute_cache/CP.htm.zip
Downloaded file ./statute_cache/BC.htm.zip
Downloaded file ./statute_cache/FI.htm.zip
Downloaded file ./statute_cache/CR.htm.zip
Downloaded file ./statute_cache/ES.htm.zip
Downloaded file ./statute_cache/PE.htm.zip
Downloaded file ./statute_cache/PW.htm.zip
Downloaded file ./statute_cache/ED.htm.zip
Downloaded file ./statute_cache/LA.htm.zip
Downloaded file ./statute_cache/NR.htm.zip
Downloaded file ./statute_cache/PR.htm.zip
Downloaded file ./statute_cache/UT.htm.zip
Downloaded file ./statute_cache/TX.htm.zip
Downloaded file ./statute_cache/CV.htm.zip
Downloaded file ./statute_cache/WA.htm.zip
Downloaded file ./statute_cache/LG.htm.zip
Downloaded file ./statute_cache/TN.htm.zip
Downloaded file ./statute_cache/HS.htm.zip
Downloaded file ./statute_cache/OC.htm.zip
Downloaded file ./statute_cache/IN.htm.zip
Downloaded file ./statute_cache/GV.htm.zip
Downloaded file ./statute_cache/SD.htm.zip
\n
Sec. 11.1827.  COMMUNITY LAND TRUST.  (a)  In this section, "community land trust" means a community land trust created or designated under Section 373B.002, Local Government Code.
(b)  In addition to any other exemption to which the trust may be entitled, a community land trust is entitled to an exemption from taxation by a taxing unit of land owned by the trust, together with the housing units located on the land if they are owned 
by the trust, if:
(1)  the trust:
(A)  meets the requirements of a charitable organization provided by Sections 11.18(e) and (f);
(B)  owns the land for the purpose of leasing the land and selling or leasing the housing units located on the land as provided by Chapter 373B, Local Government Code; and
(C)  engages exclusively in the sale or lease of housing as described by Paragraph (B) and related activities, except that the trust may also engage in the development of low-income and moderate-income housing; and
(2)  the exemption is adopted by the governing body of the taxing unit before July 1 in the manner provided by law for official action by the body.
(c)  Property owned by a community land trust may not be exempted under Subsection (b) after the third anniversary of the date the trust acquires the property unless the trust is offering to sell or lease or is leasing the property as provided by Chapter 3
73B, Local Government Code.
(d)  A community land trust entitled to an exemption from taxation by a taxing unit under Subsection (b) is also entitled to an exemption from taxation by the taxing unit of any real or tangible personal property the trust owns and uses in the administrati
on of its acquisition, construction, repair, sale, or leasing of property.  To qualify for an exemption under this subsection, property must be used exclusively by the trust, except that another person may use the property for activities incidental to the 
trust\'s use that benefit the beneficiaries of the trust.
(e)  To receive an exemption under this section, a community land trust must annually have an audit prepared by an independent auditor.  The audit must include:
(1)  a detailed report on the trust\'s sources and uses of funds; and
(2)  any other information required by the governing body of the municipality or county that created or designated the trust under Section 373B.002, Local Government Code.
(f)  Not later than the 180th day after the last day of the community land trust\'s most recent fiscal year, the trust must deliver a copy of the audit required by Subsection (e) to:
(1)  the governing body of the municipality or county or an entity designated by the governing body; and
(2)  the chief appraiser of the appraisal district in which the property subject to the exemption is located.\nAdded by Acts 2011, 82nd Leg., R.S., Ch. 383 (S.B. 402), Sec. 2, eff. January 1, 2012.
```

---
## HTTP
You can also do (an?/a?) http request instead of using cache.
This would be the done using the flag: `--query w`
```bash
python3 tx_statutes.py --source tx --statute 11.1827 --query w
```
