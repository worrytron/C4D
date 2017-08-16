DIALOG ESPNPipelineMenu
{
	NAME MAIN_DIALOG; CENTER_V; SCALE_H;

	TAB ID_STATIC
	{
		SELECTION_TABS;
		SCALE_H;

		GROUP FIRST_TAB
		{
			NAME FIRST_TAB_NAME; 
			ALIGN_TOP; 
			CENTER_H;
			COLUMNS 1;
			SIZE 600, 200;
			SPACE 4, 4;

			GROUP FIRST_TAB_GRP_01
			{
				ALIGN_TOP;
				CENTER_H;
				COLUMNS 2;
				SPACE 4, 16;
				BORDERSIZE 10,10,10,30;
				BORDERSTYLE BORDER_GROUP_IN;

				STATICTEXT LBL_PROD_NAME { NAME LBL_PROD_NAME; CENTER_V; ALIGN_LEFT; SIZE 200, 0; }
				COMBOBOX DRP_PROD_NAME   { CENTER_V; ALIGN_LEFT; SIZE 580, 0;}

				STATICTEXT LBL_PROJ_NAME { NAME LBL_PROJ_NAME; ALIGN_TOP; ALIGN_LEFT; }
				GROUP GRP_PROJ
				{
					ALIGN_TOP;
					ALIGN_LEFT;
					ROWS 3;

					EDITTEXT TXT_PROJ_NAME { ALIGN_LEFT; SIZE 600, 0; }
					COMBOBOX DRP_PROJ_NAME { NAME DRP_PROJ_NAME; ALIGN_LEFT; SIZE 580, 0; }
					CHECKBOX CHK_EXISTING  { NAME CHK_EXISTING; ALIGN_LEFT; SIZE 600, 10;}
				}

				STATICTEXT LBL_SCENE_NAME  { NAME LBL_SCENE_NAME; ALIGN_TOP; ALIGN_LEFT; }
				EDITTEXT TXT_SCENE_NAME    { ALIGN_LEFT; SIZE 200, 0; }

				STATICTEXT LBL_FRAMERATE   { NAME LBL_FRAMERATE; CENTER_V; ALIGN_LEFT; ALIGN_TOP; }
				RADIOGROUP RDO_FRAMERATE
				{
					ALIGN_LEFT;

					GROUP
					{
						COLUMNS 3;
						RADIOGADGET RDO_FRAMERATE_24 { NAME RDO_FRAMERATE_24; CENTER_H; }
						RADIOGADGET RDO_FRAMERATE_30 { NAME RDO_FRAMERATE_30; CENTER_H; }
						RADIOGADGET RDO_FRAMERATE_60 { NAME RDO_FRAMERATE_60; CENTER_H; }
					}
				}
			}

			GROUP FIRST_TAB_GRP_03
			{
				ALIGN_TOP;
				CENTER_H;
				COLUMNS 2;
				SPACE 4, 4;
				BORDERSIZE 10,10,10,10;
				BORDERSTYLE BORDER_GROUP_IN;

				STATICTEXT LBL_PREVIEW_PROJ { NAME LBL_PREVIEW_PROJ; ALIGN_TOP; ALIGN_LEFT; SIZE 200, 0; }
				EDITTEXT TXT_PREVIEW_PROJ   { ALIGN_LEFT; SIZE 600, 0; }

				STATICTEXT LBL_PREVIEW_FILE { NAME LBL_PREVIEW_FILE; ALIGN_TOP; ALIGN_LEFT; }
				EDITTEXT TXT_PREVIEW_FILE   { ALIGN_LEFT; SIZE 600, 0; }
			}

			GROUP FIRST_TAB_GRP_04
			{
				ALIGN_TOP;
				FIT_H;
				SPACE 4, 4;
				SIZE 820, 0;
				ROWS 3;

				SEPARATOR FIRST_TAB_SEP_01    { SCALE_H; SIZE 820, 0; }
				BUTTON BTN_NEWPROJ_EXEC       { NAME BTN_NEWPROJ_EXEC; SIZE 788, 33; ALIGN_TOP; }
				BUTTON BTN_HELP_EXEC          { NAME BTN_HELP_EXEC; SIZE 788, 15; ALIGN_TOP; }
			}
		}

		GROUP SAVE_RENAME_TAB
		{
			NAME SAVE_RENAME_TAB;
			ALIGN_TOP;
			FIT_H;
			COLUMNS 1;
			BORDERSTYLE BORDER_GROUP_IN;
			BORDERSIZE 10,10,10,10;

			GROUP NULL
			{
				CENTER_H;
				COLUMNS 1;
				BUTTON SAVE_BACKUP_EXEC      { NAME SAVE_BACKUP_EXEC; SIZE 800, 100; }
			}

			GROUP NULL
			{
				CENTER_H;
				COLUMNS 2;

				BUTTON RENAME_EXEC           { NAME RENAME_EXEC; SIZE 380, 33; }
				BUTTON RELINK_TEXTURES_EXEC  { NAME RELINK_TEXTURES_EXEC; SIZE 380, 33; }
				BUTTON BTN_CREATE_OBJBUFFERS { NAME BTN_CREATE_OBJBUFFERS; SIZE 380, 33; }
				BUTTON BTN_VERSIONUP         { NAME BTN_VERSIONUP; CENTER_H; SIZE 380, 33; }
				BUTTON BTN_SUBMIT            { NAME BTN_SUBMIT; CENTER_H; SIZE 380, 33; }
			}
		}

		GROUP SECOND_TAB
		{
			NAME SECOND_TAB_NAME;
			ALIGN_TOP;
			CENTER_H;
			COLUMNS 3;
			SPACE 4, 10;
			BORDERSIZE 0,5,0,0;

			GROUP SECOND_TAB_GRP_02
			{
				NAME LBL_TAKE_UTILS;
				ROWS 4;
				SIZE 375, 0;
				BORDERSIZE 10,10,10,10;
				BORDERSTYLE BORDER_GROUP_IN;

				BUTTON BTN_NEWTAKE        { NAME BTN_NEWTAKE; CENTER_H; SIZE 325, 94; }

			}

		
			GROUP SECOND_TAB_GRP_01
			{
				NAME LBL_OUTPUT_PATHS;
				ROWS 4;
				SIZE 375, 0;
				BORDERSIZE 10,10,10,10;
				BORDERSTYLE BORDER_GROUP_IN;

				GROUP PRESET_BOX_01
				{
					NAME LBL_PRESET_BOX;
					COLUMNS 2;
					SIZE 325, 12;
					COMBOBOX DRP_PRES_NAME    { CENTER_V; ALIGN_LEFT; SIZE 250, 12; }
					BUTTON BTN_SET_PRESET     { NAME BTN_SET_PRESET; CENTER_H; }
				}
				BUTTON BTN_SETOUTPUT      { NAME BTN_SETOUTPUT; CENTER_H; SIZE 325, 21; }
				BUTTON BTN_PNG_OUTPUT     { NAME BTN_PNG_OUTPUT; CENTER_H; SIZE 325, 21; }
				BUTTON BTN_EXR_OUTPUT     { NAME BTN_EXR_OUTPUT; CENTER_H; SIZE 325, 21; }
			}
		}

		GROUP THIRD_TAB
		{
			NAME THIRD_TAB_NAME;
			ALIGN_TOP;
			CENTER_H;
			ROWS 2;
			SIZE 600, 0;

			GROUP THIRD_TOP
			{

				GROUP TEAM_SWITCH_GRP
				{
					NAME TEAM_SWITCH_GRP;
					ROWS 3;
					ALIGN_TOP;
					BORDERSIZE 10,10,10,10;
					BORDERSTYLE BORDER_GROUP_IN;
					SPACE 4, 10;

					GROUP THIRD_TAB_GRP_01
					{
						COLUMNS 5;
						BORDERSIZE 20,0,0,0;
						STATICTEXT LBL_HOME_TRICODE { NAME LBL_HOME_TRICODE; ALIGN_RIGHT; SIZE 110, 0; }
						EDITTEXT   TXT_HOME_TRICODE { ALIGN_LEFT; SIZE 100, 0; }
						COLORFIELD VEC_HOME_COLOR_P { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
						COLORFIELD VEC_HOME_COLOR_S { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
						COLORFIELD VEC_HOME_COLOR_T { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
					}

					GROUP THIRD_TAB_GRP_02
					{
						COLUMNS 5;
						BORDERSIZE 20,0,0,0;
						STATICTEXT LBL_AWAY_TRICODE { NAME LBL_AWAY_TRICODE; ALIGN_RIGHT; SIZE 110, 0; }
						EDITTEXT   TXT_AWAY_TRICODE { ALIGN_LEFT; SIZE 100, 0; }
						COLORFIELD VEC_AWAY_COLOR_P { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
						COLORFIELD VEC_AWAY_COLOR_S { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
						COLORFIELD VEC_AWAY_COLOR_T { ALIGN_LEFT; NOBRIGHTNESS; NOCOLOR; }
					}
					
					GROUP THIRD_TAB_GROUP_03
					{
						ROWS 2;
						BORDERSIZE 90,0,0,0;
						CHECKBOX IS_MATCHUP { NAME IS_MATCHUP; SIZE 150, 0; }
						BUTTON TEAM_SWITCH_EXEC { NAME TEAM_SWITCH_EXEC; SIZE 266, 33; }
					}
				}

				GROUP AUTO_UTILS_GRP
				{
					NAME AUTO_UTILS_GRP;
					ROWS 6;
					ALIGN_TOP;
					BORDERSIZE 10,10,10,10;
					BORDERSTYLE BORDER_GROUP_IN;
					SPACE 4, 0;

					BUTTON HOME_PRIMARY_EXEC { NAME HOME_PRIMARY_EXEC; SIZE 200, 13; }
					BUTTON HOME_SECONDARY_EXEC { NAME HOME_SECONDARY_EXEC; SIZE 200, 13; }
					BUTTON HOME_TERTIARY_EXEC { NAME HOME_TERTIARY_EXEC; SIZE 200, 13; }

					BUTTON AWAY_PRIMARY_EXEC { NAME AWAY_PRIMARY_EXEC; SIZE 200, 13; }
					BUTTON AWAY_SECONDARY_EXEC { NAME AWAY_SECONDARY_EXEC; SIZE 200, 13; }
					BUTTON AWAY_TERTIARY_EXEC { NAME AWAY_TERTIARY_EXEC; SIZE 200, 13; }
				}
			}

			GROUP THIRD_BOT
			{
				BUTTON AUTOMATION_HELP_EXEC { NAME AUTOMATION_HELP_EXEC; SIZE 750, 15; }
			}

		}

	}
}