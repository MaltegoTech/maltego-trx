Alias = "maltego.Alias"
ASNumber = "maltego.AS"
BuiltwithTechnology = "maltego.BuiltWithTechnology"
BuiltWithRelationship = "maltego.BuiltWithRelationship"
CircularArea = "maltego.CircularArea"
Company = "maltego.Company"
Device = "maltego.Device"
DNS = "maltego.DNSName"
Document = "maltego.Document"
Domain = "maltego.Domain"
Email = "maltego.EmailAddress"
FlickrAffiliation = "maltego.AffiliationFlickr"
GPS = "maltego.GPS"
Hash = "maltego.Hash"
Hashtag = "maltego.Hashtag"
Image = "maltego.Image"
IPAddress = "maltego.IPv4Address"
Location = "maltego.Location"
MX = "maltego.MXRecord"
MyspaceAffiliation = "maltego.AffiliationMyspace"
Namechk = "maltego.Namechk"
Netblock = "maltego.Netblock"
NS = "maltego.NSRecord"
Organization = "maltego.Organization"
Person = "maltego.Person"
PhoneNumber = "maltego.PhoneNumber"
Phrase = "maltego.Phrase"
Port = "maltego.Port"
Sentiment = "maltego.Sentiment"
StockSymbol = "maltego.StockSymbol"
Tweet = "maltego.Twit"
TwitterAffiliation = "maltego.AffiliationTwitter"
TwitterList = "maltego.TwitterUserList"
UniqueID = "maltego.UniqueIdentifier"
URL = "maltego.URL"
Website = "maltego.Website"
WebTitle = "maltego.WebTitle"

# {entityName: {version2PropertyName: version3PropertyName,...}}
entity_property_map = {
    "maltego.Person": {"firstname": "person.firstnames", "lastname": "person.lastname"},
    "maltego.Domain": {"whois": "whois-info"},
    "maltego.IPv4Address": {"whois": "whois-info"},
    "maltego.URL": {"maltego.v2.value.property": "short-title", "theurl": "url", "fulltitle": "title"},
    "maltego.Document": {"maltego.v2.value.property": "title", "link": "url", "metainfo": "document.meta-data"},
    "maltego.Location": {"area": "location.area", "countrysc": "url", "long": "longitude", "lat": "latitude"},
    "maltego.PhoneNumber": {
        "countrycode": "phonenumber.countrycode", "citycode": "phonenumber.citycode",
        "areacode": "phonenumber.areacode", "lastnumbers": "phonenumber.lastnumbers"
    },
    "maltego.affiliation.Spock": {
        "network": "affiliation.network", "uid": "affiliation.uid", "profile_url": "affiliation.profile-url",
        "spock_websites": "spock.websites"
    },
    "maltego.affiliation": {
        "network": "affiliation.network", "uid": "affiliation.uid", "profile_url": "affiliation.profile-url"
    },
    "maltego.Service": {"banner": "banner.text", "port": "port.number"},
    "maltego.Alias": {"properties.alias": "alias"},
    "maltego.Device": {"properties.device": "device"},
    "maltego.GPS": {"properties.gps": "gps.coordinate"},
    "maltego.CircularArea": {"area": "radius"},
    "maltego.Image": {"properties.image": "description", "fullImage": "url"},
    "maltego.NominatimLocation": {"properties.nominatimlocation": "nominatimlocation"},
    "maltego.BuiltWithTechnology": {"properties.builtwithtechnology": "builtwith.technology"},
    "maltego.FacebookObject": {"properties.facebookobject": "facebook.object"}
}


def translate_legacy_property_name(entity_type, v2_property):
    """Function maps a legacy version 2 entity property name to version 3 entity property name"""
    return entity_property_map .get(entity_type, {}).get(v2_property)
