<img src="https://quantkiosk.com/assets/img/qk-logo.png" height="40" />

>[!IMPORTANT]
> **FREE API keys are now enabled for all accounts. Get yours [here](https://quantkiosk.com?ref=github-qkiosk-py)!!**
>
> Paid plans will be open in the coming weeks as we finish backfill and add more features!

## Python Client

Official interface to [QUANTkiosk](https://quantkiosk.com) data api.

<img width="753" alt="image" src="https://github.com/user-attachments/assets/5d328e70-cb5a-4a8e-b0f2-2bf4d6de8d72" />

### Features
* A true extension of `python` - use the tools you are productive with.
* Integrated symbology to easily map entities and instruments.
* Limited dependencies to ensure easy installation and no conflicts.
* Access to all data endpoints, including Ownership and Fundamentals.
* Parallel API requests for large downloads in a fraction of the time.
* Internal caching to minimize external requests and data usage

### Installation
# install from [PyPi](https://pypi.org/project/qkiosk/)
```bash
pip install qkiosk
```

# install from github (development version)
```bash
pip install git+https://github.com/quantkiosk/qkiosk-py.git
```

### Set up your API key
All access to live and historical data requires a valid `QK_API_KEY` to be set. To get your
**FREE** key go to the [account page](https://www.quantkiosk.com/account). If you have not signed up for an account, you can
enter your email and your account key will be good for 250 credits a day. More than enough to explore and
make use of the API. If you need more data, just select an appropriate plan.

```python
## Set your API key in the python session after you've load the freshly installed package

import qkiosk as qk
qk.set_apikey("<YOUR_API_KEY>")
```

>[!TIP]
>```bash
>## you can also set up your key in your shell to avoid having to set it in python
>## this is more permanent and definitely how you would do it in production
>
>export QK_API_KEY=<YOUR_API_KEY>
>```

>[!TIP]
>You don't actually need a key to get started with the package. We've included datasets that represent what each of the endpoints
>return to help get a feel for the breadth and depth of what QK does.
>
>```python
>import qkiosk as qk
>qk.data?
>
># Signature: qk.data()
># Docstring:
>#     Data sets in ‘qkiosk’:
># 
>#     crox        Crocs Institutional Holders Details By Issuer
>#     deshaw      D.E. Shaw Institutional Ownership Details (Including Submanagers)
>#     nke         Nike (NKE) Insider Ownership Data
>#     pershing    Pershing Square Beneficial and Activist Details
>#     pfe         Pfizer (PFE) Revenue Data
>#     sgcap       SG Capital Institutional Ownership Details (Aggregated)
># 
># e.g. load_pershing() loads as a Pandas DataFrame
>```

## Get Started

### Symbology drives everything.

The most important part of any institutional data is getting the mappings correct. The best hedge funds take having a security master for granted. It is also
an incredible pain point that firms spend millions a year to manage, or tens of thousands (or more!) to buy.

Once you have access to a proper symbology - you won't understand how you ever lived without it.

**QUANTkiosk** is solving this once and for all by creating an open *entity and security* master to help
leverage our data with as little effort as possible.  You can read more about our project on the site, but in short, everything
within the API is referenced by a **QKID**. To make that _easy_ we have some helper functions. Both search and conversion
is part of the batteries included mindset of QK.

Obviously you likely have _some_ identifier to begin with. Most often this is a ticker, like **AAPL** or **MRK**. You can use this
to map to a **QKID**, but you can even search right from your `python` session. This is especially useful for things that
don't have ticker - e.g. a hedge fund you want to track.

```python
>import qkiosk as qk
# You know the ticker or cik? Just use direct conversion:
qk.ticker("AAPL")
#                      AAPL 
# 0000320193.0000.001S5N8V8

qk.ticker("AAPL")
# qkid: ['0000320193.0000.001S5N8V8']

qk.ticker(["AAPL","ABNB"])
# qkid: ['0000320193.0000.001S5N8V8', '0001559720.0000.001Y2XS16']

qk.cik(78003).to_name()
# ["PFIZER INC"]

qk.cik(78003).to_permid()
# ["4295904722"]

# use fuzzy search for a company like Alibaba
BABA = qk.search_co("alibaba")
#
# 1: ALIBABA GROUP HOLDING-SP ADR
# 2: ALITHYA USA INC
# 3: ALIGNMENT HEALTHCARE INC
# 4: ALTI GLOBAL INC
# 5: ALLY FINANCIAL INC
# 6: ALLEGIANT TRAVEL CO
#
#Selection: 1
BABA
# ALIBABA GROUP HOLDING-SP ADR 
#    0001577552.0400.006G2JWB1
```

You can also search for fund managers in a similar way
```python
janest = qk.search_mgr("jane street")

# 1: JANE STREET GROUP LLC
# 2: JANNEY MONTGOMERY SCOTT LLC
# 3: JANA PARTNERS MANAGEMENT LP
# 4: JANNEY CAPITAL MANAGEMENT LLC
# 5: JOURNEY STRATEGIC WEALTH LLC
# 6: JAMES INVESTMENT RESEARCH INC

# Selection: 1

janest
#     JANE STREET GROUP LLC 
# 0001595888.0000.E0000Y7E8 
> 

```

There is *way* more to know about the **QKID**, but this is the README, so we will move along.  Be sure to try conversion tools like `qk.ticker("AAPL")` and `qk.cik(320187).to_ticker()` to see the power
for yourself.

>[!NOTE]
>A **QKID** is actually a just a unique combination of entity, class and an instrument:
>
>  *[ENTITY].[CLS].[INSTRUMENT]*
>
>The entity is most often the **CIK**, the instrument is an OpenFIGI **FIGI**, and the class is something that helps to quickly identify what this
>instrument is.  Pretty simple, but unlike most everything you might have seen in a security master.
>
>Alibaba will serve as an example of what this looks like in practice
>```
> BABA
> # ALIBABA GROUP HOLDING-SP ADR 
> # 0001577552.0400.006G2JWB1
>```
> - *[ENTITY]* the 10 digit CIK assigned by the SEC to any entity that files in the US. Even foreign firms need one at times.
> - *[CLS]* is the classification of the instrument. In this case the 0400 is an ADR tradable in the US. 0000 is used for the common equity - often Class A Ordinary, and there are many others available
> - *[INSTRUMENT]* is the variable portion of the FIGI from OpenFIGI, which is quickly becoming the de-facto identifier - covering a billion+ instruments
>
>For entities that do not have instruments (e.g. a hedge fund or a CEO), we create a unique instrument part to allow for consistency (e.g. **E0000Y7E8** like in Jane Street's case above).

## Get some data.

QK's job is to let you do _your_ job. Mapped, point-in-time, and even auditable - all from within your preferred platform - is how we make that happen. 
To get a feel for this, we'll take a look at two foundational areas - **Ownership** and **Fundamentals**:

- *Universe*
- *Institutional Ownership*
- *Insider Ownership*
- *Activist Ownership*
- *Fundamentals*

Let's get started

### Start with a Universe

In all institutional settings, you are almost always working with a universe. This is nothing more than a collection
of firms or instruments that are part of a strategy. These are often defined by a set of rules - e.g. minimum market cap and
price, some limits on minimum daily volume, etc.

To get you started, we have created a set of universe definitions to showcase the design and data behind **QUANTkiosk**. We'll elaborate on methodologies at another time,
but these represent the most widely held companies amongst institutional investors. From the top 100 to 3000 firms (**QK100**, **QK1000**, **QK3000**, with **QK2000** being those firms less widley held than
the top 1000)

```python
qk100 = qk.univ("QK100")
qk100[:5]
```

```python
qkid: ['0000001800.0000.001S5N9M6',
 '0000002488.0000.001S5NN36',
 '0000004962.0000.001S5P034',
 '0000006951.0000.001S5NMM7',
 '0000008670.0000.001S82KF6']
```

```python
qk100[:5].to_ticker()

qk100[:5].to_name()

qk100[:5].to_cik()
```

```python
# ticker
['ABT', 'AMD', 'AXP', 'AMAT', 'ADP']

# name
['ABBOTT LABORATORIES',
 'ADVANCED MICRO DEVICES',
 'AMERICAN EXPRESS CO',
 'APPLIED MATERIALS INC',
 'AUTOMATIC DATA PROCESSING']

# cik
['1800', '2488', '4962', '6951', '8670']

```

Of course, not everything you might want to request is a tradable entity.  In fact, the _owners_ of the above universe are private firms in many cases.

### Institutional Ownership

What they call "smart money". Certain asset managers (those with over $100mm in reportable assets) are obliged to disclose their positions at the end of each quarter. The `qkiosk` package includes two
examples - `deshaw` and `sgcap`, both which provide good documentation on what the structure of the data is. For our purposes, lets just request some data to see how easy it is to get a picture of what held last quarter.

First, well get the manager that became particularly popular in the pandemic. The are a very large multistrat player, who reports for both the asset manager business and the securities business. To get a good feel for
what they are doing for the investing side, it is very useful to be able to see submanager details, which QK does very well.

```python
citadel = qk.search_mgr("citadel")
#  1: CITADEL ADVISORS LLC
#  2: CITADEL INVESTMENT ADVISORY INC.
#  3: CIT BANK NA WEALTH MANAGEMENT
#  4: CITY STATE BANK
#  5: CIC WEALTH LLC
#  6: CITIZENS FINANCIAL GROUP INC/RI
#  7: CITY CENTER ADVISORS LLC
#  8: CITY HOLDING CO
#  9: CITIZENS NATIONAL BANK TRUST DEPARTMENT
# 10: CI PRIVATE WEALTH LLC
# Selection: 1

citadel
#      CITADEL ADVISORS LLC 
# 0001423053.0000.E0000UI19
```
Now that we have our QKID, we can use it in the function called `qk.institutional`. Interface matters a lot to us. If you don't notice how easy it is to use, it is because we've done our job.
```
ca_202402_202501 = qk.institutional(citadel, yyyyqq=202501, qtrs=4, agg=False)
# fetching 0001423053 for 202501 ...done.
# fetching 0001423053 for 202404 ...done.
# fetching 0001423053 for 202403 ...done.
# fetching 0001423053 for 202402 ...done.


```


It's easy to see what Citadel Securities (otherManager==1 in this case) is holding, how much it has changed, and even see positions they no longer have.
```
# first set display width to size of terminal if needed
pd.set_option('display.width',0)

# force pandas to render all columns - you can also set this globally in Pandas
with pd.option_context('display.max_columns', None):
     print(ca[ca["otherManager"]==1])
```

```
                  filerName                                       filing submissionType  reportPeriod  filedDate  inclMgrs                 issuer titleOfClass  issuerSIC issuerSector  \
1      CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-25-005687.txt         13F-HR      20250331   20250515         1  1 800 FLOWERS COM INC         CL A     5990.0           CD   
2      CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-25-005687.txt         13F-HR      20250331   20250515         1  1 800 FLOWERS COM INC         CL A     5990.0           CD   
3      CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-25-005687.txt         13F-HR      20250331   20250515         1  1 800 FLOWERS COM INC         CL A     5990.0           CD   
5      CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-25-005687.txt         13F-HR      20250331   20250515         1       10X GENOMICS INC     CL A COM     3826.0           HC   
6      CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-25-005687.txt         13F-HR      20250331   20250515         1       10X GENOMICS INC     CL A COM     3826.0           HC   
...                     ...                                          ...            ...           ...        ...       ...                    ...          ...        ...          ...   
20300  CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-24-008735.txt         13F-HR      20240630   20240814         1          ZYMEWORKS INC          COM     2834.0           HC   
20301  CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-24-008735.txt         13F-HR      20240630   20240814         1          ZYMEWORKS INC          COM     2834.0           HC   
20302  CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-24-008735.txt         13F-HR      20240630   20240814         1              ZYNEX INC          COM     3845.0           HC   
20303  CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-24-008735.txt         13F-HR      20240630   20240814         1              ZYNEX INC          COM     3845.0           HC   
20304  CITADEL ADVISORS LLC  edgar/data/1423053/0000950123-24-008735.txt         13F-HR      20240630   20240814         1              ZYNEX INC          COM     3845.0           HC   

      issuerTicker                 issuerQkid    value  shrsOrPrnAmt putCall shrsOrPrnAmtType invDiscretion  votingAuthSole  votingAuthShared  votingAuthNone  portWgt  hasOtherManager  \
1             FLWS  0001084869.0000.001S60YV4        0             0     NaN               SH          DFND               0                 0               0      0.0             True   
2             FLWS  0001084869.000C.001S60YV4   487340         82600    CALL               SH          DFND           82600                 0               0  9.2e-07             True   
3             FLWS  0001084869.000P.001S60YV4   274350         46500     PUT               SH          DFND           46500                 0               0  5.2e-07             True   
5              TXG  0001770787.0000.007WX14Y9   703961         80637     NaN               SH          DFND           80637                 0               0 1.33e-06             True   
6              TXG  0001770787.000C.007WX14Y9  1250136        143200    CALL               SH          DFND          143200                 0               0 2.37e-06             True   
...            ...                        ...      ...           ...     ...              ...           ...             ...               ...             ...      ...              ...   
20300         ZYME  0001937653.000C.019XSYC98   114034         13400    CALL               SH          DFND           13400                 0               0  2.3e-07             True   
20301         ZYME  0001937653.000P.019XSYC98    71484          8400     PUT               SH          DFND            8400                 0               0  1.4e-07             True   
20302        ZYXIQ  0000846475.0000.001S7T7V0        0             0     NaN               SH          DFND               0                 0               0      0.0             True   
20303        ZYXIQ  0000846475.000C.001S7T7V0        0             0    CALL               SH          DFND               0                 0               0      0.0             True   
20304        ZYXIQ  0000846475.000P.001S7T7V0        0             0     PUT               SH          DFND               0                 0               0      0.0             True   

       otherManager           otherManagerName otherManagerFileNumber  QtrsHeld  QOQSshPrnAmt  QOQValue  QOQPortWgt newOrDel  
1               1.0  Citadel Securities GP LLC               28-18870         2        -73419   -599833   -1.04e-06      DEL  
2               1.0  Citadel Securities GP LLC               28-18870        23         37500    118873     2.9e-07      NaN  
3               1.0  Citadel Securities GP LLC               28-18870        20         24400     93793     2.1e-07      NaN  
5               1.0  Citadel Securities GP LLC               28-18870         8       -230384  -3762301   -6.39e-06      NaN  
6               1.0  Citadel Securities GP LLC               28-18870        22        102300    662812    1.35e-06      NaN  
...             ...                        ...                    ...       ...           ...       ...         ...      ...  
20300           1.0  Citadel Securities GP LLC               28-18870        19         -7900   -110042      -2e-07      NaN  
20301           1.0  Citadel Securities GP LLC               28-18870         7         -2700    -45288      -8e-08      NaN  
20302           1.0  Citadel Securities GP LLC               28-18870         3        -89709  -1109700   -2.14e-06      DEL  
20303           1.0  Citadel Securities GP LLC               28-18870         1         -1800    -22266      -4e-08      DEL  
20304           1.0  Citadel Securities GP LLC               28-18870         4          -200     -2474        -0.0      DEL  

[62433 rows x 30 columns]

```

There are of course, a million ways to use this data - and we promise to share videos as well as deep dives as we move forward. We also would love to have anyone using the API share how they 
are discovering insights into what the "Who's Who of Wall Street" are up to each quarter.

We can also explore details of company holders, large shareholders, and even corporate insiders with similar speed and ease.

```python
# all holders of NVDA in 2022 Q1
nvda_holders = qk.holders(qk.ticker("NVDA"), yyyyqq=202201)

# NVDA insiders - (e.g. CEO, Sr.EVP, ...)
nvda_insiders = qk.insider(qk.ticker("NVDA"), yyyyqq=202201)

# Large NVDA block holders for 2022 (above 5%)
nvda_lg = qk.beneficial(qk.ticker("NVDA"), yyyyqq=202200)
```

### Fundamentals

Fundamentals data is the lifeblood of a company. While prices are observable, financials are much harder to source
consistently or correctly.  We source directly from filings, in a way only people who have used this data for
investment at scale know how to do.

Let's dig into a quick example to show off what you can do with a few lines of code.

```python
# There are hundreds of line items that are generally used - though 10s of 1000s of GAAP items are available.
#
# To see common ones we currently map you can use our reference function qk.fncodes

qk.fncodes()
```

```
    stmt  QKCODE                                              label
0     BS    CASH                          Cash and Cash Equivalents
1     BS     AOC                             Assets - Other Current
2     BS     ATC                                  Assets - Current 
3     BS    AOCI                       Accumulated Other Net Income
4     BS    AONC             Other Net Assets Including Intangibles
..   ...     ...                                                ...
169   IS   STKDP                  Dividends Paid - Per Common Share
170   IS      XO                           Total Operating Expenses
171   IS  EPSDDO  Diluted Earnings Loss Per Share - Discontinued...
172   IS   EPSDO  Basic Earnings Loss Per Share - Discontinued O...
173   IS    NIDO          Net Loss Income - Discontinued Operations

[174 rows x 3 columns]
```

From here, lets find Net Income (code NI) for UBER

```python
uber_ni = qk.fn(qk.ticker("UBER"), "NI")

uber_ni.to_df().tail()
```
```

         cik  acceptance_time stmt item     filed       fpb       fpe  fqd  fp  fqtr     cyqtr           fq          fytd           ttm           ann  rstmt
 28  1543151   20250214160634   IS   NI  20250214  20240101  20241231 92.0  FY     4  20250331 6883000000.0  9856000000.0  9856000000.0  9856000000.0      0
 29  1543151   20250507160717   IS   NI  20250507  20250101  20250331 90.0  Q1     1  20250630 1776000000.0  1776000000.0 12286000000.0           NaN      0
 30  1543151   20250806160750   IS   NI  20250806  20250401  20250630 91.0  Q2     2  20250930 1355000000.0  3131000000.0 10196000000.0           NaN      0
 31  1543151   20251104160441   IS   NI  20251104  20250701  20250930 92.0  Q3     3  20251231 6626000000.0  9757000000.0 13870000000.0           NaN      0
 32  1543151   20260213160817   IS   NI  20260213  20250101  20251231 92.0  FY     4  20260331  296000000.0 10053000000.0 10053000000.0 10053000000.0      0

```
<img width="1051" alt="image" src="https://github.com/user-attachments/assets/06d42814-99dc-4ba7-96de-ea72166bbb93" />

You can also easily see where this data comes from using our state of the art auditing tools
```
# show all 40 columns
qk.fn(qk.ticker("UBER"), "NI").full().to_df().tail()

## Python Support COMING SOON!
#qk.fn(qk.ticker("UBER"), "NI").to_df().tail().highlight(5).qk_audit()
```

<img width="1119" alt="image" src="https://github.com/user-attachments/assets/903a6d09-9f5d-416b-a484-449a7504ddc3" />






