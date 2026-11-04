-- =====================================================================
-- NutriSib – Magazin: conturi de client (Supabase)
-- Rulează O SINGURĂ DATĂ în Supabase → SQL Editor → New query → Run.
-- Nu șterge și nu modifică nimic din tabelele existente.
-- =====================================================================

-- 1) Datele de livrare/facturare salvate în cont (precompletare la comandă)
create table if not exists public.magazin_clienti (
  id            uuid primary key references auth.users(id) on delete cascade,
  nume          text, prenume text, telefon text,
  judet         text, localitate text, adresa text, cod_postal text,
  firma_denumire text, firma_cui text, firma_regcom text, firma_adresa text,
  actualizat    timestamptz not null default now()
);

-- 2) Profilul nutrițional opțional (date privind sănătatea – art. 9 GDPR, doar cu consimțământ)
create table if not exists public.magazin_profil_nutritional (
  user_id          uuid primary key references auth.users(id) on delete cascade,
  greutate_actuala numeric(5,1), greutate_dorita numeric(5,1), inaltime smallint,
  an_nastere       smallint, sex text check (sex in ('Feminin','Masculin')),
  consimtamant     timestamptz not null,
  actualizat       timestamptz not null default now()
);

-- 3) Istoricul comenzilor (scris DOAR de server, din webhook-ul Stripe)
create table if not exists public.magazin_comenzi (
  id         text primary key,
  user_id    uuid references auth.users(id) on delete set null,
  email      text not null,
  status     text not null,
  creata     timestamptz not null,
  platita    timestamptz,
  produse    jsonb not null,
  subtotal   numeric(10,2) not null, transport numeric(10,2) not null, total numeric(10,2) not null, vp_total numeric(8,2),
  livrare    jsonb, firma jsonb, factura jsonb
);
create index if not exists magazin_comenzi_email_idx on public.magazin_comenzi (lower(email));
create index if not exists magazin_comenzi_user_idx on public.magazin_comenzi (user_id);

-- Row Level Security: fiecare client își vede/modifică doar propriile date
alter table public.magazin_clienti enable row level security;
alter table public.magazin_profil_nutritional enable row level security;
alter table public.magazin_comenzi enable row level security;

drop policy if exists "client: citire proprie" on public.magazin_clienti;
create policy "client: citire proprie" on public.magazin_clienti for select using (auth.uid() = id);
drop policy if exists "client: inserare proprie" on public.magazin_clienti;
create policy "client: inserare proprie" on public.magazin_clienti for insert with check (auth.uid() = id);
drop policy if exists "client: modificare proprie" on public.magazin_clienti;
create policy "client: modificare proprie" on public.magazin_clienti for update using (auth.uid() = id) with check (auth.uid() = id);

drop policy if exists "profil: citire propriu" on public.magazin_profil_nutritional;
create policy "profil: citire propriu" on public.magazin_profil_nutritional for select using (auth.uid() = user_id);
drop policy if exists "profil: inserare propriu" on public.magazin_profil_nutritional;
create policy "profil: inserare propriu" on public.magazin_profil_nutritional for insert with check (auth.uid() = user_id);
drop policy if exists "profil: modificare propriu" on public.magazin_profil_nutritional;
create policy "profil: modificare propriu" on public.magazin_profil_nutritional for update using (auth.uid() = user_id) with check (auth.uid() = user_id);
drop policy if exists "profil: stergere propriu" on public.magazin_profil_nutritional;
create policy "profil: stergere propriu" on public.magazin_profil_nutritional for delete using (auth.uid() = user_id);

-- Comenzile: clientul le vede pe ale lui – inclusiv cele plasate fără cont, cu același e-mail
drop policy if exists "comenzi: citire proprie" on public.magazin_comenzi;
create policy "comenzi: citire proprie" on public.magazin_comenzi for select
  using (auth.uid() = user_id or lower(email) = lower(coalesce(auth.jwt() ->> 'email', '')));
-- (nicio politică de insert/update/delete: doar cheia service_role, folosită de server, poate scrie)

grant select, insert, update on public.magazin_clienti to authenticated;
grant select, insert, update, delete on public.magazin_profil_nutritional to authenticated;
grant select on public.magazin_comenzi to authenticated;
