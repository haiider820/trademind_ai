-- Apply this migration if you already executed 001_initial_schema.sql

create table if not exists public.device_tokens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  token text not null unique,
  platform text not null check (platform in ('android', 'ios', 'web')),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.device_tokens enable row level security;

do $$
begin
  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'device_tokens' and policyname = 'device_tokens_select_own'
  ) then
    create policy "device_tokens_select_own"
    on public.device_tokens
    for select
    using (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'device_tokens' and policyname = 'device_tokens_insert_own'
  ) then
    create policy "device_tokens_insert_own"
    on public.device_tokens
    for insert
    with check (auth.uid() = user_id);
  end if;

  if not exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename = 'device_tokens' and policyname = 'device_tokens_update_own'
  ) then
    create policy "device_tokens_update_own"
    on public.device_tokens
    for update
    using (auth.uid() = user_id)
    with check (auth.uid() = user_id);
  end if;
end $$;

alter table public.news add column if not exists external_id text;
create unique index if not exists idx_news_external_id on public.news(external_id);

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
as $$
begin
  insert into public.profiles (id, name, role, subscription)
  values (new.id, coalesce(new.raw_user_meta_data->>'name', ''), 'user', 'free')
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
after insert on auth.users
for each row execute procedure public.handle_new_user();
