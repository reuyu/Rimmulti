from review_setup import *
def main():
    s=(PREVQ/'RunnerTemplate.cs.txt').read_text(encoding='utf-8-sig')
    s=s.replace('args.Length!=2','args.Length!=3').replace('return Run(args[1]);','System.Threading.Thread.CurrentThread.CurrentCulture=System.Globalization.CultureInfo.GetCultureInfo(args[2]);return Run(args[1]);')
    s=s.replace('var cases=(JObject)input["cases"];','var cases=(JObject)input["cases"];var expectedCases=(JObject)input["expected_canonical_cases"];')
    s=s.replace('string bytes=ContentProfileProvider.SerializeCanonicalJson(dto);', '''string transport=ContentProfileProvider.SerializeCanonicalJson(dto,false);
      var transportDecoded=ContentProfileProvider.DeserializeCanonicalJson(transport);var transportChecks=new List<object>();Compare(p.Value,JToken.FromObject(transportDecoded),"",transportChecks);Save(p.Name+".transport.json",transport);Save(p.Name+".transport_checks.json",JsonConvert.SerializeObject(transportChecks,Formatting.Indented));
      ContentProfileProvider.CanonicalNormalize(dto);var normalizeChecks=new List<object>();Compare(expectedCases[p.Name],JToken.FromObject(dto),"",normalizeChecks);Save(p.Name+".normalize_checks.json",JsonConvert.SerializeObject(normalizeChecks,Formatting.Indented));
      string bytes=ContentProfileProvider.SerializeCanonicalJson(dto,true);''')
    s=s.replace('Compare(p.Value,semantics,"",checks);','Compare(expectedCases[p.Name],semantics,"",checks);')
    s=s.replace('outputs[p.Name]=bytes;decoded[p.Name]=semantics;', '''outputs[p.Name]=bytes;decoded[p.Name]=semantics;
      var fresh=ContentProfileProvider.DeserializeCanonicalJson(before);string freshBefore=ContentProfileProvider.SerializeCanonicalJson(fresh,false);string freshCanonical=ContentProfileProvider.SerializeCanonicalJson(fresh,true);string freshAfter=ContentProfileProvider.SerializeCanonicalJson(fresh,false);
      Check("CANONICAL_"+p.Name+"_NORMALIZE",freshCanonical==bytes&&freshAfter==bytes,"Explicit normalize/default canonical boundary and in-place mutation match independent normal policy");
      Save(p.Name+".mutation_observation.json",JsonConvert.SerializeObject(new{before_transport_sha256=Hash(Utf8.GetBytes(freshBefore)),after_transport_sha256=Hash(Utf8.GetBytes(freshAfter)),in_place_bytes_changed=freshBefore!=freshAfter,ordered_children_compared=true},Formatting.Indented));
      if(p.Name=="BASE"||p.Name=="NORMAL_REVISION_B"){string reason;bool valid=ContentProfileProvider.ValidateContract(restored,out reason);Check("POSITIVE_CONTRACT_"+p.Name,valid&&reason=="","Fully declared normal manifest positive helper return;not admission proof");}''')
    s=s.replace('set_scope="Collector-declared Def sets; serializer does not normalize order independently"','set_scope="R6 production canonical boundary normal distinct keys;ordered list and multiplicity kept"')
    s=s.replace('"QA pure codec run "+runId','"QA fresh R6 positive codec-contract run "+runId')
    s=s.replace('Console.WriteLine("Runtime="+Environment.Version+', 'Console.WriteLine("Culture="+System.Threading.Thread.CurrentThread.CurrentCulture.Name+" Runtime="+Environment.Version+')
    s=s.replace('pure codec controls. Historical leaf65','R6 pure positive codec-contract controls. Historical leaf65')
    (Q/'RunnerTemplate.cs.txt').write_text(s,encoding='utf-8');print('Fresh R6 runner template created;only allowed codec/positive helper and DTO metadata')
if __name__=='__main__':main()
