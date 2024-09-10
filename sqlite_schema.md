# simple schema for sqlite things

|    Article/Chapter(table)    |
| statute(uuid) |  text(uuid)| section_data(char)| effective_date |

| EXPLAINED |
| statute(uuid) -> [table with statute text and dates]|
| text(uuid) -> [table with statute text & date effective]|
| section_data(char) [some code that indicates how many levels there are currently in this section]|
| effective_date(datetime) |


| for example, this couldd be something like Transportation Code 544.002 as of Tue 10 Sep 2024 04:20:31 PM CDT|

## Example 0 of section_data: 

    Sec. 544.002.  PLACING AND MAINTAINING TRAFFIC-CONTROL DEVICE.  (a)  To implement this subtitle, the Texas Department of Transportation may place 
    and maintain a traffic-control device on a state highway as provided by the manual and specifications adopted under Section 544.001.  The Texas De
    partment of Transportation may provide for the placement and maintenance of the device under Section 221.002.
    (b)  To implement this subtitle or a local traffic ordinance, a local authority may place and maintain a traffic-control device on a highway under
    the authority's jurisdiction.  The traffic-control device must conform to the manual and specifications adopted under Section 544.001.
    (c)  A local authority may not place or maintain a traffic-control device on a highway under the jurisdiction of the Texas Department of Transport
    ation without that department's permission, except as authorized under Section 545.3561.
    Acts 1995, 74th Leg., ch. 165, Sec. 1, eff. Sept. 1, 1995.Amended by: 
    Acts 2011, 82nd Leg., R.S., Ch. 216 (H.B. 109), Sec. 1, eff. September 1, 2011.

```sql
SELECT section_data FROM Transportation_code WHERE section = '544.002'
```
```text
> abc
```

## Example 1 of section_data:

    Sec. 544.003.  AUTHORITY TO DESIGNATE THROUGH HIGHWAY AND STOP AND YIELD INTERSECTIONS.  (a)  The Texas Transportation Commission may:
    (1)  designate a state or county highway as a through highway and place a stop or yield sign at a specified entrance;  or
    (2)  designate an intersection on a state or county highway as a stop intersection or a yield intersection and place a sign at one or more entranc
    es to the intersection.
    (b)  A local authority may:
    (1)  designate a highway under its jurisdiction as a through highway and place a stop or yield sign at a specified entrance;  or
    (2)  designate an intersection on a highway under its jurisdiction as a stop intersection or a yield intersection and place a sign at one or more 
    entrances to the intersection.
    (c)  The stop or yield sign indicating the preferential right-of-way must:
    (1)  conform to the manual and specifications adopted under Section 544.001;  and
    (2)  be located:
    (A)  as near as practicable to the nearest line of the crosswalk;  or
    (B)  in the absence of a crosswalk, at the nearest line of the roadway.
    Acts 1995, 74th Leg., ch. 165, Sec. 1, eff. Sept. 1, 1995.

```sql
SELECT section_data FROM Transportation_code WHERE section = '544.003'
```
```text
> a12b12c12AB
```
