SELECT
    m."Nome_Municipio" AS nome_municipio,
    m."Unidade_Geografica" AS uf,
    c."Nome_Urna" AS nome_urna_candidato,
    c."FK_Sigla_Partido" AS sigla_partido,
    p."Num_Partido" AS numero_partido,
    v."Zona" AS zona_eleitoral,
    v."Votos_Nominais_Candidato" AS votos_candidato
FROM public.votacao_candidato_municipio_zona AS v
LEFT JOIN public.candidato AS c ON v."FK_Num_Candidato" = c."Num_Candidato"
LEFT JOIN public.municipio AS m ON v."FK_Cod_Municipio" = m."Cod_IBGE"
LEFT JOIN public.partido AS p ON c."FK_Sigla_Partido" = p."Sigla_Partido"
WHERE v."Votos_Nominais_Candidato" IS NOT NULL AND v."Votos_Nominais_Candidato" > 0;