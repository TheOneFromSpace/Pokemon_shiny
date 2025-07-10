use master
drop database if exists PokemonShiny
create database PokemonShiny
use PokemonShiny

create table account(
    username varchar(20) not null,
    password varchar(max) not null,
    
    constraint pk_account primary key (username)
);

create table pokedex(
    dexnr bigint not null,
    pokemonname varchar(max) not null,
    
    constraint pk_pokedex primary key (dexnr)
);

create table pokeball(
    ballnr int not null,
    ballname varchar(max) not null,
    
    constraint pk_ball primary key (ballnr)
);

create table game(
    gameid int not null,
    gamename varchar(max) not null,
    generationid int not null,
    
    constraint pk_game primary key (gameid)
);

create table huntingmethod(
    methodid int not null,
    methodname varchar(max) not null,
    baseodds numeric(4) default 4096,
	notes varchar(max) null
    
    constraint pk_method primary key (methodid)
);

create table methodpergame(
    gameid int not null,
    methodid int not null,
    
    constraint pk_game_method primary key (gameid, methodid),
    constraint fk_game_per_method_method foreign key (methodid) references huntingmethod(methodid),
    constraint fk_game_per_method_game foreign key (gameid) references game(gameid)
);



create table caughtshiny(
    shinyid bigint not null,
    pokemon bigint not null,
    gender varchar(max) null,
    nickname varchar(max) null,
    pokeball int null,
    username varchar(20) not null,
    otname varchar(20) null,
    game_caught int not null,
    method int not null,
    date_caught date null,
    time_caught time null,
    time_taken time null,
    encounters int null,
	video_link varchar(50) null,
    notes varchar(50) null,
    
    constraint pk_caughtshiny primary key (shinyid),
    constraint fk_caughtshiny_pokedex foreign key (pokemon) references pokedex(dexnr),
    constraint fk_caughtshiny_pokeball foreign key (pokeball) references pokeball(ballnr),
    constraint fk_caughtshiny_account foreign key (username) references account(username),
    constraint fk_caughtshiny_game foreign key (game_caught) references game(gameid),
    constraint fk_caughtshiny_method foreign key (method) references huntingmethod(methodid)
);

